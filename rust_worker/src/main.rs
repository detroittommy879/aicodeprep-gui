use anyhow::{Context, Result};
use clap::Parser;
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
    selected_files: Vec<String>,
    output_file: String,
    format: String,
    prompt: String,
    prompt_to_top: bool,
    prompt_to_bottom: bool,
    cwd: String,
    secret_mode: bool,
    placeholder_prefix: String,
}

#[derive(Debug, Serialize)]
struct Response {
    ok: bool,
    files_processed: usize,
    secret_map_file: Option<String>,
    error: Option<String>,
}

fn is_binary_file(path: &Path) -> bool {
    let data = match fs::read(path) {
        Ok(bytes) => bytes,
        Err(_) => return false,
    };
    let chunk = if data.len() > 1024 { &data[..1024] } else { &data[..] };
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

fn pseudonymize_content(content: &str, prefix: &str) -> (String, HashMap<String, String>) {
    let mut map: HashMap<String, String> = HashMap::new();
    let mut output = content.to_string();

    let assignment_regex = Regex::new(
        r#"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']([A-Za-z0-9_\-\/+=]{16,})[\"']"#,
    )
    .expect("valid regex");

    let mut replacements: Vec<(String, String)> = Vec::new();
    for captures in assignment_regex.captures_iter(content) {
        if let Some(m) = captures.get(2) {
            let secret = m.as_str();
            if looks_like_secret(secret) {
                let placeholder = placeholder_for(secret, prefix);
                replacements.push((secret.to_string(), placeholder.clone()));
                map.insert(placeholder, secret.to_string());
            }
        }
    }

    let aws_regex =
        Regex::new(r#"\b(AKIA[0-9A-Z]{16})\b"#).expect("valid AWS access key regex");
    for captures in aws_regex.captures_iter(content) {
        if let Some(m) = captures.get(1) {
            let secret = m.as_str();
            let placeholder = placeholder_for(secret, prefix);
            replacements.push((secret.to_string(), placeholder.clone()));
            map.insert(placeholder, secret.to_string());
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

fn process_request(request: Request) -> Result<Response> {
    let cwd = PathBuf::from(&request.cwd);
    let output_path = PathBuf::from(&request.output_file);

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
        secret_map_file,
        error: None,
    })
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
