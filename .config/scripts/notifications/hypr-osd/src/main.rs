mod bluetooth;
mod brightness;
mod notification;
mod volume;
mod workspace;

use std::env;

fn socket_path(socket: &str) -> String {
    let sig = env::var("HYPRLAND_INSTANCE_SIGNATURE").expect("HYPRLAND_INSTANCE_SIGNATURE not set");
    let runtime = env::var("XDG_RUNTIME_DIR").unwrap_or_else(|_| "/run/user/1000".to_string());

    let xdg_path = format!("{runtime}/hypr/{sig}/{socket}");
    let tmp_path = format!("/tmp/hypr/{sig}/{socket}");

    if std::path::Path::new(&xdg_path).exists() {
        xdg_path
    } else {
        tmp_path
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    match args.get(1).map(|s| s.as_str()) {
        Some("volume")     => volume::run(&args[2..]),
        Some("brightness") => brightness::run(&args[2..]),
        None               => daemon(),
        _                  => eprintln!("usage: hypr-osd [volume|brightness] [args]"),
    }
}

fn daemon() {
    let workspace = std::thread::spawn(|| workspace::run(&socket_path));
    let bluetooth = std::thread::spawn(|| bluetooth::run());

    workspace.join().unwrap();
    bluetooth.join().unwrap();
}
