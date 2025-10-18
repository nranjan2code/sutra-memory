fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Copy storage proto for compilation
    tonic_build::configure()
        .build_server(false)
        .compile(
            &["../sutra-storage/proto/storage.proto"],
            &["../sutra-storage/proto"],
        )?;
    Ok(())
}
