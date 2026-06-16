# Manual Rust Worker Builds

Use this when GitHub Actions is unavailable and you need to manually build the Rust worker binaries that ship inside the Python package.

The app looks for bundled workers under:

```text
aicodeprep_gui/rust/bin/<platform>/aicp-rust-worker
aicodeprep_gui/rust/bin/<platform>/aicp-rust-worker.exe
```

Supported platform folder names:

```text
darwin-aarch64
darwin-x86_64
linux-aarch64
linux-x86_64
windows-x86_64
```

Prefer the GitHub Actions workflow when possible. It builds these automatically and verifies the package contains them. Manual builds are mostly for emergencies.

## Prerequisites

Run all commands from the `aicodeprep-gui` repo root.

Install Rust with `rustup` if needed:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup update stable
```

On macOS, install Xcode command line tools if needed:

```bash
xcode-select --install
```

On Ubuntu, install build tools if needed:

```bash
sudo apt update
sudo apt install -y build-essential pkg-config
```

Before every release build, run the worker tests:

```bash
cargo test --manifest-path rust_worker/Cargo.toml
```

## macOS Apple Silicon

This builds the `darwin-aarch64` worker for M1/M2/M3/M4 Macs.

```bash
rustup target add aarch64-apple-darwin
cargo build --release --target aarch64-apple-darwin --manifest-path rust_worker/Cargo.toml
mkdir -p aicodeprep_gui/rust/bin/darwin-aarch64
cp rust_worker/target/aarch64-apple-darwin/release/aicp-rust-worker aicodeprep_gui/rust/bin/darwin-aarch64/aicp-rust-worker
chmod +x aicodeprep_gui/rust/bin/darwin-aarch64/aicp-rust-worker
```

## macOS Intel

Best option: build on an Intel Mac.

```bash
rustup target add x86_64-apple-darwin
cargo build --release --target x86_64-apple-darwin --manifest-path rust_worker/Cargo.toml
mkdir -p aicodeprep_gui/rust/bin/darwin-x86_64
cp rust_worker/target/x86_64-apple-darwin/release/aicp-rust-worker aicodeprep_gui/rust/bin/darwin-x86_64/aicp-rust-worker
chmod +x aicodeprep_gui/rust/bin/darwin-x86_64/aicp-rust-worker
```

Apple Silicon Macs can often cross-build this target too, but verify the result on an Intel Mac if you are shipping it.

## Ubuntu Linux ARM64

This builds the `linux-aarch64` worker for ARM64 Ubuntu machines.

```bash
rustup target add aarch64-unknown-linux-gnu
cargo build --release --target aarch64-unknown-linux-gnu --manifest-path rust_worker/Cargo.toml
mkdir -p aicodeprep_gui/rust/bin/linux-aarch64
cp rust_worker/target/aarch64-unknown-linux-gnu/release/aicp-rust-worker aicodeprep_gui/rust/bin/linux-aarch64/aicp-rust-worker
chmod +x aicodeprep_gui/rust/bin/linux-aarch64/aicp-rust-worker
```

## Ubuntu Linux x86_64

This builds the `linux-x86_64` worker for typical Intel/AMD Linux machines.

```bash
rustup target add x86_64-unknown-linux-gnu
cargo build --release --target x86_64-unknown-linux-gnu --manifest-path rust_worker/Cargo.toml
mkdir -p aicodeprep_gui/rust/bin/linux-x86_64
cp rust_worker/target/x86_64-unknown-linux-gnu/release/aicp-rust-worker aicodeprep_gui/rust/bin/linux-x86_64/aicp-rust-worker
chmod +x aicodeprep_gui/rust/bin/linux-x86_64/aicp-rust-worker
```

## Windows x86_64

Build from PowerShell on 64-bit Windows with the MSVC Rust toolchain installed.

```powershell
rustup target add x86_64-pc-windows-msvc
cargo build --release --target x86_64-pc-windows-msvc --manifest-path rust_worker\Cargo.toml
New-Item -ItemType Directory -Force aicodeprep_gui\rust\bin\windows-x86_64
Copy-Item rust_worker\target\x86_64-pc-windows-msvc\release\aicp-rust-worker.exe aicodeprep_gui\rust\bin\windows-x86_64\aicp-rust-worker.exe
```

## Collecting Binaries From Other Machines

If you build on separate machines, copy only the final worker binary back into the matching platform directory. Do not commit `rust_worker/target/`.

Example from your main release machine:

```bash
scp macbook:/path/to/aicodeprep-gui/rust_worker/target/aarch64-apple-darwin/release/aicp-rust-worker aicodeprep_gui/rust/bin/darwin-aarch64/aicp-rust-worker
scp ubuntu-arm:/path/to/aicodeprep-gui/rust_worker/target/aarch64-unknown-linux-gnu/release/aicp-rust-worker aicodeprep_gui/rust/bin/linux-aarch64/aicp-rust-worker
```

After copying, make Unix workers executable:

```bash
chmod +x aicodeprep_gui/rust/bin/darwin-*/*
chmod +x aicodeprep_gui/rust/bin/linux-*/*
```

## Build The Python Package With Manual Workers

Once all available worker binaries are in `aicodeprep_gui/rust/bin/<platform>/`, build the Python package:

```bash
python -m pip install --upgrade build
python -m build
```

Or with `uv`:

```bash
uv build --no-sources
```

## Verify The Package Contains Workers

Check the wheel contents:

```bash
python - <<'PY'
import zipfile
from pathlib import Path

wheel = next(Path("dist").glob("*.whl"))
with zipfile.ZipFile(wheel) as zf:
    for name in sorted(zf.namelist()):
        if "aicodeprep_gui/rust/bin/" in name:
            print(name)
PY
```

Expected output should include whichever platform binaries you manually copied, ideally all five:

```text
aicodeprep_gui/rust/bin/darwin-aarch64/aicp-rust-worker
aicodeprep_gui/rust/bin/darwin-x86_64/aicp-rust-worker
aicodeprep_gui/rust/bin/linux-aarch64/aicp-rust-worker
aicodeprep_gui/rust/bin/linux-x86_64/aicp-rust-worker
aicodeprep_gui/rust/bin/windows-x86_64/aicp-rust-worker.exe
```

## Smoke Test A Local Worker

From a machine that has the built binary, run:

```bash
./aicodeprep_gui/rust/bin/linux-aarch64/aicp-rust-worker --help
```

Replace `linux-aarch64` with the platform you are testing. On Windows:

```powershell
.\aicodeprep_gui\rust\bin\windows-x86_64\aicp-rust-worker.exe --help
```

