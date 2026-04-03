use notify_rust::{Hint, Notification};
use std::env;
use std::io::{BufRead, BufReader, Read, Write};
use std::os::unix::net::UnixStream;

fn socket_path(socket: &str) -> String {
    let sig = env::var("HYPRLAND_INSTANCE_SIGNATURE")
        .expect("HYPRLAND_INSTANCE_SIGNATURE not set");
    let runtime = env::var("XDG_RUNTIME_DIR")
        .unwrap_or_else(|_| "/run/user/1000".to_string());

    let xdg_path = format!("{runtime}/hypr/{sig}/{socket}");
    let tmp_path = format!("/tmp/hypr/{sig}/{socket}");

    if std::path::Path::new(&xdg_path).exists() {
        xdg_path
    } else {
        tmp_path
    }
}

fn active_workspace() -> (i32, String) {
    let mut stream = UnixStream::connect(socket_path(".socket.sock")).unwrap();
    stream.write_all(b"j/activeworkspace").unwrap();

    let mut response = Vec::new();
    let mut buf = [0u8; 8192];
    loop {
        let n = stream.read(&mut buf).unwrap_or(0);
        response.extend_from_slice(&buf[..n]);
        if n == 0 || n < 8192 { break; }
    }

    let response = String::from_utf8_lossy(&response);

    let id = response
        .split("\"id\":")
        .nth(1)
        .and_then(|s| s.split(',').next())
        .and_then(|s| s.trim().parse().ok())
        .unwrap_or(0);

    let name = response
        .split("\"name\": \"")
        .nth(1)
        .and_then(|s| s.split('"').next())
        .unwrap_or("?")
        .to_string();

    (id, name)
}

fn send_notification(id: i32, name: &str) {
    Notification::new()
        .appname("workspace")
        .id(9992)
        .timeout(1000)
        .summary(&format!("Workspace {id}"))
        .body(name)
        .hint(Hint::Custom(
            "x-canonical-private-synchronous".to_string(),
            "workspace".to_string(),
        ))
        .show()
        .unwrap();
}

fn main() {
    let stream = UnixStream::connect(socket_path(".socket2.sock"))
        .expect("could not connect to Hyprland event socket");

    for line in BufReader::new(stream).lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => break,
        };

        // events arrive as "workspace>>Algorithms"
        if line.starts_with("workspace>>") {
            let (id, name) = active_workspace();
            send_notification(id, &name);
        }
    }
}
