#!/usr/bin/env rust

use clap::{Parser, Subcommand};

mod grid {
    tonic::include_proto!("grid");
}

#[derive(Parser)]
#[command(name = "sutra-grid-cli")]
#[command(about = "CLI for Sutra Grid Master", long_about = None)]
struct Cli {
    #[arg(short, long, default_value = "http://localhost:7002")]
    master: String,
    
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// List all registered agents
    ListAgents,
    
    /// Get cluster status
    Status,
    
    /// Spawn a storage node on an agent
    Spawn {
        /// Agent ID to spawn the node on
        #[arg(short, long)]
        agent: String,
        
        /// Port for the storage node
        #[arg(short, long)]
        port: u32,
        
        /// Storage path for the node
        #[arg(short, long, default_value = "/tmp/storage")]
        storage_path: String,
        
        /// Memory limit in MB
        #[arg(short, long, default_value = "512")]
        memory: u64,
    },
    
    /// Stop a storage node
    Stop {
        /// Node ID to stop
        #[arg(short, long)]
        node: String,
        
        /// Agent ID owning the node
        #[arg(short, long)]
        agent: String,
    },
    
    /// Get status of a specific storage node
    NodeStatus {
        /// Node ID to query
        #[arg(short, long)]
        node: String,
    },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    
    let mut client = grid::grid_master_client::GridMasterClient::connect(cli.master.clone()).await?;
    
    match cli.command {
        Commands::ListAgents => {
            let response = client.list_agents(grid::Empty {}).await?;
            let agents = response.into_inner();
            
            println!("📋 Registered Agents ({}):", agents.agents.len());
            println!();
            
            for agent in agents.agents {
                println!("🖥️  Agent: {}", agent.agent_id);
                println!("   Hostname: {}", agent.hostname);
                println!("   Platform: {}", agent.platform);
                println!("   Status: {}", agent.status);
                println!("   Storage Nodes: {}/{}", agent.current_storage_nodes, agent.max_storage_nodes);
                println!("   Last Heartbeat: {} seconds ago", 
                    std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)?
                        .as_secs()
                        .saturating_sub(agent.last_heartbeat)
                );
                
                if !agent.storage_nodes.is_empty() {
                    println!("   Active Nodes:");
                    for node in agent.storage_nodes {
                        println!("     - {} (PID: {}, Status: {}, Endpoint: {})", 
                            node.node_id, node.pid, node.status, node.endpoint);
                    }
                }
                println!();
            }
        }
        
        Commands::Status => {
            let response = client.get_cluster_status(grid::Empty {}).await?;
            let status = response.into_inner();
            
            println!("📊 Cluster Status");
            println!("================");
            println!("Total Agents: {}", status.total_agents);
            println!("Healthy Agents: {}", status.healthy_agents);
            println!("Total Storage Nodes: {}", status.total_storage_nodes);
            println!("Running Storage Nodes: {}", status.running_storage_nodes);
            println!("Overall Status: {}", status.status);
        }
        
        Commands::Spawn { agent, port, storage_path, memory } => {
            println!("📦 Spawning storage node on agent {}...", agent);
            
            let response = client.spawn_storage_node(grid::SpawnRequest {
                agent_id: agent.clone(),
                port,
                storage_path,
                memory_limit_mb: memory,
            }).await?;
            
            let result = response.into_inner();
            
            if result.success {
                println!("✅ Storage node spawned successfully!");
                println!("   Node ID: {}", result.node_id);
                println!("   Endpoint: {}", result.endpoint);
            } else {
                println!("❌ Failed to spawn storage node");
                println!("   Error: {}", result.error_message);
            }
        }
        
        Commands::Stop { node, agent } => {
            println!("🛑 Stopping storage node {}...", node);
            
            let response = client.stop_storage_node(grid::StopRequest {
                node_id: node.clone(),
                agent_id: agent,
            }).await?;
            
            let result = response.into_inner();
            
            if result.success {
                println!("✅ Storage node stopped successfully!");
            } else {
                println!("❌ Failed to stop storage node");
                println!("   Error: {}", result.error_message);
            }
        }
        
        Commands::NodeStatus { node } => {
            let response = client.get_storage_node_status(grid::NodeId {
                node_id: node.clone(),
            }).await?;
            
            let status = response.into_inner();
            
            println!("📦 Storage Node: {}", status.node_id);
            println!("   Status: {}", status.status);
            println!("   PID: {}", status.pid);
            println!("   Endpoint: {}", status.endpoint);
        }
    }
    
    Ok(())
}
