const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("BEXToken", function () {
  let bexToken;
  let owner;
  let user1;
  let user2;
  
  const INITIAL_SUPPLY = 130_000_000n;
  const DECIMALS = 18n;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();
    
    const BEXToken = await ethers.getContractFactory("BEXToken");
    bexToken = await BEXToken.deploy(owner.address);
    await bexToken.waitForDeployment();
  });

  describe("部署", function () {
    it("应该正确设置代币基本信息", async function () {
      expect(await bexToken.name()).to.equal("BEX");
      expect(await bexToken.symbol()).to.equal("BEX");
      expect(await bexToken.decimals()).to.equal(18);
    });

    it("应该将初始供应量分配给部署者", async function () {
      const expectedSupply = INITIAL_SUPPLY * (10n ** DECIMALS);
      expect(await bexToken.totalSupply()).to.equal(expectedSupply);
      expect(await bexToken.balanceOf(owner.address)).to.equal(expectedSupply);
    });

    it("应该正确设置合约拥有者", async function () {
      expect(await bexToken.owner()).to.equal(owner.address);
    });
  });

  describe("mint函数", function () {
    it("合约拥有者应该能够增发代币", async function () {
      const mintAmount = 1000n;
      const expectedMintAmount = mintAmount * (10n ** DECIMALS);
      
      await expect(bexToken.mint(user1.address, mintAmount))
        .to.emit(bexToken, "Transfer")
        .withArgs(ethers.ZeroAddress, user1.address, expectedMintAmount);
      
      expect(await bexToken.balanceOf(user1.address)).to.equal(expectedMintAmount);
    });

    it("非拥有者不能调用mint函数", async function () {
      await expect(
        bexToken.connect(user1).mint(user2.address, 1000n)
      ).to.be.revertedWithCustomError(bexToken, "OwnableUnauthorizedAccount");
    });

    it("不能向零地址增发代币", async function () {
      await expect(
        bexToken.mint(ethers.ZeroAddress, 1000n)
      ).to.be.revertedWith("BEX: cannot mint to zero address");
    });

    it("不能增发零数量的代币", async function () {
      await expect(
        bexToken.mint(user1.address, 0n)
      ).to.be.revertedWith("BEX: amount must be greater than 0");
    });
  });

  describe("辅助函数", function () {
    it("getTotalSupply应该返回正确的总供应量", async function () {
      expect(await bexToken.getTotalSupply()).to.equal(INITIAL_SUPPLY);
      
      // 增发一些代币后再次检查
      await bexToken.mint(user1.address, 5000n);
      expect(await bexToken.getTotalSupply()).to.equal(INITIAL_SUPPLY + 5000n);
    });

    it("getBalance应该返回正确的余额", async function () {
      expect(await bexToken.getBalance(owner.address)).to.equal(INITIAL_SUPPLY);
      expect(await bexToken.getBalance(user1.address)).to.equal(0n);
      
      // 增发代币后检查余额
      await bexToken.mint(user1.address, 1000n);
      expect(await bexToken.getBalance(user1.address)).to.equal(1000n);
    });
  });

  describe("ERC20标准功能", function () {
    it("应该支持代币转账", async function () {
      const transferAmount = 1000n * (10n ** DECIMALS);
      
      await expect(bexToken.transfer(user1.address, transferAmount))
        .to.emit(bexToken, "Transfer")
        .withArgs(owner.address, user1.address, transferAmount);
      
      expect(await bexToken.balanceOf(user1.address)).to.equal(transferAmount);
    });

    it("应该支持授权和transferFrom", async function () {
      const approveAmount = 1000n * (10n ** DECIMALS);
      
      await bexToken.approve(user1.address, approveAmount);
      expect(await bexToken.allowance(owner.address, user1.address)).to.equal(approveAmount);
      
      await bexToken.connect(user1).transferFrom(owner.address, user2.address, approveAmount);
      expect(await bexToken.balanceOf(user2.address)).to.equal(approveAmount);
    });
  });
}); 