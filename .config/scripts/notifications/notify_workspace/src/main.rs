use notify_rust::{Hint, Notification};

fn main() {
    let workspace: u8 = std::env::args()
        .nth(1)
        .expect("usage: notify_workspace <number>")
        .parse()
        .expect("must be a number");

    let fallback = format!("Workspace {workspace}");
    let name = match workspace {
        1 => "Algorithms",
        2 => "Paradigms",
        3 => "Web",
        4 => "Div",
        5 => "3d Print",
        10 => "0",
        _ => &fallback,
    };

    Notification::new()
        .appname("workspace")
        .id(9992)
        .timeout(1000)
        .summary(&format!("Workspace {workspace}"))
        .body(name)
        .hint(Hint::Custom(
            "x-canonical-private-synchronous".to_string(),
            "workspace".to_string(),
        ))
        .show()
        .unwrap();
}
