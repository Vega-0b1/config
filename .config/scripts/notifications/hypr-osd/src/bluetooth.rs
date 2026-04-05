use crate::notification;
use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};

// remove ANSI escape sequences from a string
fn strip_ansi(s: &str) -> String {
    let mut out = String::new();
    let mut chars = s.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '\x1b' && chars.peek() == Some(&'[') {
            chars.next(); // consume '['
            for c2 in chars.by_ref() {
                if c2.is_ascii_alphabetic() { break; } // end of escape sequence
            }
        } else {
            out.push(c);
        }
    }
    out
}

pub fn run() {
    let mut child = Command::new("bluetoothctl")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .expect("could not start bluetoothctl");

    let _stdin = child.stdin.take(); // keep pipe open so bluetoothctl doesn't get EOF and exit
    let stdout = child.stdout.take().unwrap();

    for line in BufReader::new(stdout).lines() {
        let line = match line {
            Ok(l) => {
                let stripped = strip_ansi(&l);
                // bluetoothctl uses \r to overwrite the prompt — take the last segment
                stripped.split('\r').last().unwrap_or("").to_string()
            }
            Err(_) => break,
        };

        // events look like:
        // [CHG] Device XX:XX:XX:XX:XX:XX Connected: yes
        // [CHG] Device XX:XX:XX:XX:XX:XX Connected: no
        if line.contains("Device") && line.contains("Connected:") {
            let connected = line.contains("Connected: yes");
            let mac = line.split_whitespace().nth(2).unwrap_or("").to_string();

            let name = get_device_name(&mac);

            if connected {
                notification::send("bluetooth", 9993, 3000, "Bluetooth Connected", &name);
            } else {
                notification::send("bluetooth", 9993, 3000, "Bluetooth Disconnected", &name);
            }
        }
    }
}

fn get_device_name(mac: &str) -> String {
    let out = Command::new("bluetoothctl")
        .args(["info", mac])
        .output()
        .unwrap();

    let out = strip_ansi(&String::from_utf8_lossy(&out.stdout));

    // output contains a line like: "	Name: My Headphones"
    out.lines()
        .find(|l| l.trim_start().starts_with("Name:"))
        .and_then(|l| l.split_once("Name:"))
        .map(|(_, name)| name.trim().to_string())
        .unwrap_or_else(|| mac.to_string())
}
