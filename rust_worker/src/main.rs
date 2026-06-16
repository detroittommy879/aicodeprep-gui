use anyhow::{Context, Result};
use clap::Parser;
use ignore::{
    gitignore::{Gitignore, GitignoreBuilder},
    WalkBuilder, WalkState,
};
use regex::Regex;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

#[derive(Parser, Debug)]
struct Cli {
    #[arg(long)]
    request: PathBuf,
}

#[derive(Debug, Deserialize)]
struct Request {
    #[serde(default = "default_op")]
    op: String,
    #[serde(default)]
    selected_files: Vec<String>,
    #[serde(default)]
    output_file: String,
    #[serde(default)]
    format: String,
    #[serde(default)]
    prompt: String,
    #[serde(default)]
    prompt_to_top: bool,
    #[serde(default)]
    prompt_to_bottom: bool,
    #[serde(default)]
    cwd: String,
    #[serde(default)]
    secret_mode: bool,
    #[serde(default = "default_placeholder_prefix")]
    placeholder_prefix: String,
    #[serde(default)]
    root_dir: String,
    #[serde(default)]
    code_extensions: Vec<String>,
    #[serde(default)]
    exclude_patterns: Vec<String>,
    #[serde(default)]
    default_include_patterns: Vec<String>,
    #[serde(default = "default_max_file_size")]
    max_file_size: u64,
    #[serde(default)]
    respect_gitignore: bool,
}

#[derive(Debug, Serialize)]
struct Response {
    ok: bool,
    files_processed: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    files: Option<Vec<ScanEntry>>,
    secret_map_file: Option<String>,
    error: Option<String>,
}

#[derive(Debug, Serialize)]
struct ScanEntry {
    path: String,
    rel_path: String,
    is_checked: bool,
}

fn default_op() -> String {
    "pack".to_string()
}

fn default_placeholder_prefix() -> String {
    "REDACTED_SECRET_".to_string()
}

fn default_max_file_size() -> u64 {
    1_000_000
}

fn is_binary_file(path: &Path) -> bool {
    let data = match fs::read(path) {
        Ok(bytes) => bytes,
        Err(_) => return false,
    };
    let chunk = if data.len() > 1024 { &data[..1024] } else { &data[..] };
    if chunk.starts_with(&[0xEF, 0xBB, 0xBF])
        || chunk.starts_with(&[0xFF, 0xFE])
        || chunk.starts_with(&[0xFE, 0xFF])
        || chunk.starts_with(&[0xFF, 0xFE, 0x00, 0x00])
        || chunk.starts_with(&[0x00, 0x00, 0xFE, 0xFF])
    {
        return false;
    }
    chunk.contains(&0)
}

fn shannon_entropy(value: &str) -> f64 {
    let len = value.len() as f64;
    if len == 0.0 {
        return 0.0;
    }

    let mut counts: HashMap<char, usize> = HashMap::new();
    for ch in value.chars() {
        *counts.entry(ch).or_insert(0) += 1;
    }

    counts
        .values()
        .map(|count| {
            let p = *count as f64 / len;
            -p * p.log2()
        })
        .sum()
}

fn looks_like_secret(candidate: &str) -> bool {
    let len = candidate.len();
    if len < 16 {
        return false;
    }
    let entropy = shannon_entropy(candidate);
    entropy >= 3.4
}

fn placeholder_for(secret: &str, prefix: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(secret.as_bytes());
    let digest = hasher.finalize();
    let short_hex = format!("{:x}", digest);
    format!("{}{}", prefix, &short_hex[..12])
}

fn queue_secret_replacement(
    secret: &str,
    prefix: &str,
    replacements: &mut Vec<(String, String)>,
    map: &mut HashMap<String, String>,
    require_entropy: bool,
) {
    let trimmed = secret.trim();
    if trimmed.is_empty() {
        return;
    }
    if require_entropy && !looks_like_secret(trimmed) {
        return;
    }
    if map.values().any(|existing| existing == trimmed) {
        return;
    }

    let placeholder = placeholder_for(trimmed, prefix);
    replacements.push((trimmed.to_string(), placeholder.clone()));
    map.insert(placeholder, trimmed.to_string());
}

fn pseudonymize_content(content: &str, prefix: &str) -> (String, HashMap<String, String>) {
    let mut map: HashMap<String, String> = HashMap::new();
    let mut output = content.to_string();

    let assignment_regex = Regex::new(
        r#"(?i)\b(api[_-]?key|secret|token|password|auth[_-]?token|access[_-]?token|client[_-]?secret|private[_-]?key)\b\s*[:=]\s*[\"']?([A-Za-z0-9_\-./+=]{16,})[\"']?"#,
    )
    .expect("valid regex");

    let mut replacements: Vec<(String, String)> = Vec::new();
    for captures in assignment_regex.captures_iter(content) {
        if let Some(m) = captures.get(2) {
            queue_secret_replacement(m.as_str(), prefix, &mut replacements, &mut map, true);
        }
    }

    let aws_regex =
        Regex::new(r#"\b(AKIA[0-9A-Z]{16})\b"#).expect("valid AWS access key regex");
    for captures in aws_regex.captures_iter(content) {
        if let Some(m) = captures.get(1) {
            queue_secret_replacement(m.as_str(), prefix, &mut replacements, &mut map, false);
        }
    }

    let provider_regexes = [
        r#"\b(sk-ant-[A-Za-z0-9_\-.]{10,})\b"#,
        r#"\b(sk-(?:live|test|proj)-[A-Za-z0-9_\-.]{16,})\b"#,
        r#"\b(gh[pousr]_[A-Za-z0-9_]{20,})\b"#,
        r#"\b(xox[baprs]-[A-Za-z0-9\-]{20,})\b"#,
        r#"\b(AIza[0-9A-Za-z_\-]{20,})\b"#,
    ];
    for pattern in provider_regexes {
        let regex = Regex::new(pattern).expect("valid provider token regex");
        for captures in regex.captures_iter(content) {
            if let Some(m) = captures.get(1) {
                queue_secret_replacement(m.as_str(), prefix, &mut replacements, &mut map, false);
            }
        }
    }

    let bearer_regex = Regex::new(
        r#"(?i)\b(?:authorization|proxy-authorization)\s*:\s*bearer\s+([A-Za-z0-9_\-./+=]{16,})"#,
    )
    .expect("valid bearer token regex");
    for captures in bearer_regex.captures_iter(content) {
        if let Some(m) = captures.get(1) {
            queue_secret_replacement(m.as_str(), prefix, &mut replacements, &mut map, true);
        }
    }

    for (secret, placeholder) in replacements {
        output = output.replace(&secret, &placeholder);
    }

    (output, map)
}

fn relative_path(cwd: &Path, file_path: &Path) -> String {
    match file_path.strip_prefix(cwd) {
        Ok(rel) => rel.display().to_string(),
        Err(_) => file_path.display().to_string(),
    }
}

fn normalized_relative_path(root: &Path, file_path: &Path) -> String {
    file_path
        .strip_prefix(root)
        .unwrap_or(file_path)
        .to_string_lossy()
        .replace('\\', "/")
}

fn build_gitignore(patterns: &[String]) -> Result<Gitignore> {
    let mut builder = GitignoreBuilder::new("");
    for pattern in patterns {
        let trimmed = pattern.trim();
        if trimmed.is_empty() {
            continue;
        }
        builder
            .add_line(None, trimmed)
            .with_context(|| format!("invalid ignore pattern: {trimmed}"))?;
    }
    builder.build().context("failed to build ignore matcher")
}

fn matcher_ignores(matcher: &Gitignore, rel_path: &str, is_dir: bool) -> bool {
    matcher.matched_path_or_any_parents(rel_path, is_dir).is_ignore()
}

fn extension_or_name_matches(path: &Path, code_extensions: &[String]) -> bool {
    let file_name = path.file_name().and_then(|name| name.to_str()).unwrap_or("");
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| format!(".{}", ext.to_ascii_lowercase()))
        .unwrap_or_default();

    code_extensions.iter().any(|configured| {
        let configured = configured.to_ascii_lowercase();
        configured == extension || configured == file_name.to_ascii_lowercase()
    })
}

fn should_check_scan_entry(
    abs_path: &Path,
    rel_path: &str,
    is_dir: bool,
    include_matcher: &Gitignore,
    code_extensions: &[String],
    max_file_size: u64,
) -> bool {
    let mut is_checked = include_matcher
        .matched_path_or_any_parents(rel_path, is_dir)
        .is_ignore();

    if !is_checked && !is_dir {
        is_checked = extension_or_name_matches(abs_path, code_extensions);
    }

    if is_checked && !is_dir {
        let metadata = match fs::metadata(abs_path) {
            Ok(metadata) => metadata,
            Err(_) => return false,
        };
        if metadata.len() > max_file_size || is_binary_file(abs_path) {
            return false;
        }
    }

    is_checked
}

fn scan_directory(request: &Request) -> Result<Response> {
    let root = PathBuf::from(&request.root_dir);
    if request.root_dir.trim().is_empty() {
        anyhow::bail!("scan request missing root_dir");
    }
    if !root.is_dir() {
        anyhow::bail!("scan root is not a directory: {}", root.display());
    }

    let exclude_matcher = build_gitignore(&request.exclude_patterns)?;
    let include_matcher = build_gitignore(&request.default_include_patterns)?;
    let mut entries: Vec<ScanEntry> = Vec::new();
    let mut first_error: Option<String> = None;

    let mut builder = WalkBuilder::new(&root);
    builder
        .hidden(false)
        .parents(request.respect_gitignore)
        .ignore(request.respect_gitignore)
        .git_global(request.respect_gitignore)
        .git_ignore(request.respect_gitignore)
        .git_exclude(request.respect_gitignore)
        .threads(0);

    let walker = builder.build_parallel();
    let (sender, receiver) = std::sync::mpsc::channel::<Result<Option<ScanEntry>, String>>();

    walker.run(|| {
        let root = root.clone();
        let sender = sender.clone();
        let exclude_matcher = exclude_matcher.clone();
        let include_matcher = include_matcher.clone();
        let code_extensions = request.code_extensions.clone();
        let max_file_size = request.max_file_size;

        Box::new(move |result| {
            let entry = match result {
                Ok(entry) => entry,
                Err(error) => {
                    let _ = sender.send(Err(error.to_string()));
                    return WalkState::Continue;
                }
            };

            let path = entry.path();
            if path == root {
                return WalkState::Continue;
            }
            if entry.file_type().is_some_and(|file_type| file_type.is_symlink()) {
                return WalkState::Continue;
            }

            let is_dir = entry.file_type().is_some_and(|file_type| file_type.is_dir());
            let is_file = entry.file_type().is_some_and(|file_type| file_type.is_file());
            if !is_dir && !is_file {
                return WalkState::Continue;
            }

            let rel_path = normalized_relative_path(&root, path);
            if matcher_ignores(&exclude_matcher, &rel_path, is_dir) {
                return if is_dir {
                    WalkState::Skip
                } else {
                    WalkState::Continue
                };
            }

            let is_checked = should_check_scan_entry(
                path,
                &rel_path,
                is_dir,
                &include_matcher,
                &code_extensions,
                max_file_size,
            );
            let scan_entry = ScanEntry {
                path: path.display().to_string(),
                rel_path,
                is_checked,
            };

            if sender.send(Ok(Some(scan_entry))).is_err() {
                return WalkState::Quit;
            }
            WalkState::Continue
        })
    });
    drop(sender);

    for result in receiver {
        match result {
            Ok(Some(entry)) => entries.push(entry),
            Ok(None) => {}
            Err(error) => {
                first_error.get_or_insert(error);
            }
        }
    }

    entries.sort_by(|left, right| {
        left.rel_path
            .to_ascii_lowercase()
            .cmp(&right.rel_path.to_ascii_lowercase())
    });

    if let Some(error) = first_error {
        eprintln!("scan warning: {error}");
    }

    Ok(Response {
        ok: true,
        files_processed: entries.len(),
        files: Some(entries),
        secret_map_file: None,
        error: None,
    })
}

fn write_file_block_xml(
    output: &mut String,
    rel_path: &str,
    content: &str,
    secret_mode: bool,
    placeholder_prefix: &str,
    global_map: &mut HashMap<String, String>,
) {
    output.push_str(&format!("{}:\n<code>\n", rel_path));
    if secret_mode {
        let (redacted, file_map) = pseudonymize_content(content, placeholder_prefix);
        global_map.extend(file_map);
        output.push_str(&redacted);
    } else {
        output.push_str(content);
    }
    output.push_str("\n</code>\n\n");
}

fn write_file_block_md(
    output: &mut String,
    rel_path: &str,
    content: &str,
    secret_mode: bool,
    placeholder_prefix: &str,
    global_map: &mut HashMap<String, String>,
) {
    output.push_str(&format!("### START OF FILE {} ###\n", rel_path));
    if secret_mode {
        let (redacted, file_map) = pseudonymize_content(content, placeholder_prefix);
        global_map.extend(file_map);
        output.push_str(&redacted);
    } else {
        output.push_str(content);
    }
    output.push_str(&format!("\n### END OF FILE {} ###\n\n", rel_path));
}

fn process_pack_request(request: Request) -> Result<Response> {
    let cwd = PathBuf::from(&request.cwd);
    let output_path = PathBuf::from(&request.output_file);
    if request.output_file.trim().is_empty() {
        anyhow::bail!("pack request missing output_file");
    }

    if let Some(parent) = output_path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("failed to create output directory: {}", parent.display()))?;
    }

    let mut output = String::new();
    let mut skipped_binary: Vec<String> = Vec::new();
    let mut secret_map: HashMap<String, String> = HashMap::new();

    if !request.prompt.trim().is_empty() && request.prompt_to_top {
        output.push_str(request.prompt.trim());
        output.push_str("\n\n");
    }

    for file_path in &request.selected_files {
        let full_path = PathBuf::from(file_path);
        let rel_path = relative_path(&cwd, &full_path);

        if is_binary_file(&full_path) {
            skipped_binary.push(rel_path);
            continue;
        }

        let content = match fs::read_to_string(&full_path) {
            Ok(text) => text,
            Err(_) => {
                if request.format == "markdown" {
                    output.push_str(&format!("### START OF FILE {} ###\n", rel_path));
                    output.push_str(".. contents skipped (read error) ..\n");
                    output.push_str(&format!("### END OF FILE {} ###\n\n", rel_path));
                } else {
                    output.push_str(&format!("{}:\n<code>\n", rel_path));
                    output.push_str(".. contents skipped (read error) ..");
                    output.push_str("\n</code>\n\n");
                }
                continue;
            }
        };

        if request.format == "markdown" {
            write_file_block_md(
                &mut output,
                &rel_path,
                &content,
                request.secret_mode,
                &request.placeholder_prefix,
                &mut secret_map,
            );
        } else {
            write_file_block_xml(
                &mut output,
                &rel_path,
                &content,
                request.secret_mode,
                &request.placeholder_prefix,
                &mut secret_map,
            );
        }
    }

    if !skipped_binary.is_empty() {
        output.push('\n');
        for rel_path in skipped_binary {
            output.push_str(&format!("{} binary file skipped..\n", rel_path));
        }
    }

    if !request.prompt.trim().is_empty() && request.prompt_to_bottom {
        output.push_str("\n\n");
        output.push_str(request.prompt.trim());
    }

    let mut file = fs::File::create(&output_path)
        .with_context(|| format!("failed to create output file: {}", output_path.display()))?;
    file.write_all(output.as_bytes())
        .with_context(|| format!("failed to write output file: {}", output_path.display()))?;

    let mut secret_map_file: Option<String> = None;
    if request.secret_mode && !secret_map.is_empty() {
        let map_path = output_path
            .parent()
            .unwrap_or_else(|| Path::new("."))
            .join("secret_map.json");
        let map_json = serde_json::to_string_pretty(&secret_map)?;
        fs::write(&map_path, map_json)
            .with_context(|| format!("failed to write secret map: {}", map_path.display()))?;
        secret_map_file = Some(map_path.display().to_string());
    }

    Ok(Response {
        ok: true,
        files_processed: request.selected_files.len(),
        files: None,
        secret_map_file,
        error: None,
    })
}

fn process_request(request: Request) -> Result<Response> {
    match request.op.as_str() {
        "scan" => scan_directory(&request),
        "pack" | "" => process_pack_request(request),
        other => anyhow::bail!("unknown worker op: {other}"),
    }
}

fn main() {
    let cli = Cli::parse();

    let result: Result<Response> = (|| {
        let raw = fs::read_to_string(&cli.request)
            .with_context(|| format!("failed to read request file: {}", cli.request.display()))?;
        let request: Request =
            serde_json::from_str(&raw).context("failed to parse request JSON")?;
        process_request(request)
    })();

    match result {
        Ok(response) => {
            let json = serde_json::to_string(&response).unwrap_or_else(|_| {
                "{\"ok\":false,\"error\":\"failed to serialize response\"}".to_string()
            });
            println!("{}", json);
        }
        Err(err) => {
            let response = Response {
                ok: false,
                files_processed: 0,
                files: None,
                secret_map_file: None,
                error: Some(err.to_string()),
            };
            let json = serde_json::to_string(&response).unwrap_or_else(|_| {
                "{\"ok\":false,\"error\":\"unknown error\"}".to_string()
            });
            println!("{}", json);
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{process_request, Request};
    use std::{
        fs,
        time::{SystemTime, UNIX_EPOCH},
    };

    fn make_temp_dir() -> std::path::PathBuf {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!("aicp_worker_scan_{unique}"));
        fs::create_dir_all(&path).unwrap();
        path
    }

    fn scan_request(root_dir: &std::path::Path) -> Request {
        Request {
            op: "scan".to_string(),
            selected_files: Vec::new(),
            output_file: String::new(),
            format: String::new(),
            prompt: String::new(),
            prompt_to_top: false,
            prompt_to_bottom: false,
            cwd: String::new(),
            secret_mode: false,
            placeholder_prefix: "REDACTED_SECRET_".to_string(),
            root_dir: root_dir.display().to_string(),
            code_extensions: vec![".py".to_string()],
            exclude_patterns: vec!["excluded/".to_string()],
            default_include_patterns: vec!["README.md".to_string()],
            max_file_size: 16,
            respect_gitignore: false,
        }
    }

    fn pack_request(root_dir: &std::path::Path, output_file: &std::path::Path) -> Request {
        let file_path = root_dir.join("src").join("app.py");
        Request {
            op: "pack".to_string(),
            selected_files: vec![file_path.display().to_string()],
            output_file: output_file.display().to_string(),
            format: "xml".to_string(),
            prompt: "Review this".to_string(),
            prompt_to_top: true,
            prompt_to_bottom: false,
            cwd: root_dir.display().to_string(),
            secret_mode: false,
            placeholder_prefix: "REDACTED_SECRET_".to_string(),
            root_dir: String::new(),
            code_extensions: Vec::new(),
            exclude_patterns: Vec::new(),
            default_include_patterns: Vec::new(),
            max_file_size: 16,
            respect_gitignore: false,
        }
    }

    fn secret_pack_request(root_dir: &std::path::Path, output_file: &std::path::Path) -> Request {
        let file_path = root_dir.join("src").join("secrets.env");
        let mut request = pack_request(root_dir, output_file);
        request.selected_files = vec![file_path.display().to_string()];
        request.secret_mode = true;
        request
    }

    #[test]
    fn scan_returns_default_checked_files_and_prunes_excludes() {
        let root = make_temp_dir();
        fs::create_dir_all(root.join("src")).unwrap();
        fs::create_dir_all(root.join("excluded")).unwrap();
        fs::write(root.join("src").join("app.py"), "print(1)\n").unwrap();
        fs::write(root.join("README.md"), "# hi\n").unwrap();
        fs::write(root.join("big.py"), "x".repeat(32)).unwrap();
        fs::write(root.join("excluded").join("skip.py"), "print(0)\n").unwrap();

        let response = process_request(scan_request(&root)).unwrap();
        let files = response.files.unwrap();
        let checked: std::collections::HashMap<_, _> = files
            .iter()
            .map(|entry| (entry.rel_path.as_str(), entry.is_checked))
            .collect();

        assert_eq!(checked.get("src/app.py"), Some(&true));
        assert_eq!(checked.get("README.md"), Some(&true));
        assert_eq!(checked.get("big.py"), Some(&false));
        assert!(!checked.contains_key("excluded"));
        assert!(!checked.contains_key("excluded/skip.py"));

        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn pack_keeps_existing_aicodeprep_xml_layout() {
        let root = make_temp_dir();
        let source = root.join("src").join("app.py");
        let output = root.join(".aicp").join("context_block.md");
        fs::create_dir_all(source.parent().unwrap()).unwrap();
        fs::write(&source, "print(1)\n").unwrap();

        let response = process_request(pack_request(&root, &output)).unwrap();
        let rel_path = format!("src{}app.py", std::path::MAIN_SEPARATOR);
        assert_eq!(response.files_processed, 1);
        assert_eq!(
            fs::read_to_string(&output).unwrap(),
            format!("Review this\n\n{rel_path}:\n<code>\nprint(1)\n\n</code>\n\n")
        );

        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn pack_redacts_common_provider_and_header_tokens() {
        let root = make_temp_dir();
        let source = root.join("src").join("secrets.env");
        let output = root.join(".aicp").join("context_block.md");
        fs::create_dir_all(source.parent().unwrap()).unwrap();
        fs::create_dir_all(output.parent().unwrap()).unwrap();
        fs::write(
            &source,
            [
                "ANTHROPIC_AUTH_TOKEN=sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456",
                "Authorization: Bearer abcdefghijklmnopqrstuvwxyz1234567890",
                "GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234567890",
            ]
            .join("\n"),
        )
        .unwrap();

        let response = process_request(secret_pack_request(&root, &output)).unwrap();
        assert_eq!(response.files_processed, 1);
        let content = fs::read_to_string(&output).unwrap();

        assert!(!content.contains("sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456"));
        assert!(!content.contains("abcdefghijklmnopqrstuvwxyz1234567890"));
        assert!(!content.contains("ghp_abcdefghijklmnopqrstuvwxyz1234567890"));
        assert!(content.contains("REDACTED_SECRET_"));
        assert!(response.secret_map_file.is_some());

        let _ = fs::remove_dir_all(root);
    }
}
