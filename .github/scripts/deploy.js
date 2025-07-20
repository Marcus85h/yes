const { ethers } = require("hardhat");

async function main() {
  console.log("开始部署BEX代币合约...");

  // 获取部署者账户
  const [deployer] = await ethers.getSigners();
  console.log("部署者地址:", deployer.address);
  console.log("部署者余额:", ethers.formatEther(await deployer.provider.getBalance(deployer.address)), "ETH");

  // 部署BEX代币合约
  const BEXToken = await ethers.getContractFactory("BEXToken");
  const bexToken = await BEXToken.deploy(deployer.address);
  
  await bexToken.waitForDeployment();
  const contractAddress = await bexToken.getAddress();
  
  console.log("BEX代币合约已部署到:", contractAddress);
  
  // 获取合约信息
  const name = await bexToken.name();
  const symbol = await bexToken.symbol();
  const decimals = await bexToken.decimals();
  const totalSupply = await bexToken.totalSupply();
  const owner = await bexToken.owner();
  
  console.log("\n合约信息:");
  console.log("代币名称:", name);
  console.log("代币符号:", symbol);
  console.log("小数位数:", decimals);
  console.log("总供应量:", ethers.formatUnits(totalSupply, decimals), "BEX");
  console.log("合约拥有者:", owner);
  
  // 验证部署者余额
  const deployerBalance = await bexToken.balanceOf(deployer.address);
  console.log("部署者代币余额:", ethers.formatUnits(deployerBalance, decimals), "BEX");
  
  console.log("\n部署完成!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("部署失败:", error);
    process.exit(1);
  }); 