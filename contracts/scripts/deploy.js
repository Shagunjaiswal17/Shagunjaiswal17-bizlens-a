const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("==================================================");
  console.log("Deploying BizLens AI DocumentRegistry to:", hre.network.name);
  console.log("==================================================");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer Wallet:", deployer.address);

  const DocumentRegistry = await hre.ethers.getContractFactory("DocumentRegistry");
  const registry = await DocumentRegistry.deploy();
  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log("DocumentRegistry successfully deployed to:", contractAddress);
  console.log("Polygon Amoy Explorer URL: https://amoy.polygonscan.com/address/" + contractAddress);

  // Save deployment artifact
  const deploymentInfo = {
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    contractAddress: contractAddress,
    deployer: deployer.address,
    timestamp: new Date().toISOString()
  };

  const outPath = path.join(__dirname, "..", "deployments.json");
  fs.writeFileSync(outPath, JSON.stringify(deploymentInfo, null, 2));
  console.log("Saved deployment configuration to:", outPath);
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
