fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("proto/grid.proto")?;
    tonic_build::compile_protos("proto/agent.proto")?;
    Ok(())
}
