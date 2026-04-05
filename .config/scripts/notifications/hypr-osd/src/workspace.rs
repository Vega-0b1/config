use crate::notification;
use std::io::{BufRead, BufReader, Read, Write};
use std::os::unix::net::UnixStream;

pub fn run(socket_path: &dyn Fn(&str) -> String) {
    let stream = UnixStream::connect(socket_path(".socket2.sock"))
        .expect("could not connect to Hyprland event socket");

    for line in BufReader::new(stream).lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => break,
        };

        if line.starts_with("workspace>>") {
            let (id, name) = active_workspace(socket_path);
            notification::send("workspace", 9992, 1000, &format!("Workspace {id}"), &name);
        }
    }
}

fn active_workspace(socket_path: &dyn Fn(&str) -> String) -> (i32, String) {
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
