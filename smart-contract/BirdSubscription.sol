// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BirdSubscription {
    address public immutable owner;
    uint256 public constant PRICE = 0.001 ether;
    uint256 public constant DURATION = 30 days;

    mapping(address => uint256) public expiresAt;

    event Subscribed(address indexed user, uint256 expiresAt);

    constructor() {
        owner = msg.sender;
    }

    function subscribe() external payable {
        require(msg.value >= PRICE, "Insufficient ETH");

        uint256 start = expiresAt[msg.sender] > block.timestamp
            ? expiresAt[msg.sender]
            : block.timestamp;

        expiresAt[msg.sender] = start + DURATION;
        emit Subscribed(msg.sender, expiresAt[msg.sender]);
    }

    function isSubscribed(address user) external view returns (bool) {
        return expiresAt[user] > block.timestamp;
    }

    function withdraw() external {
        require(msg.sender == owner, "Not owner");
        payable(owner).transfer(address(this).balance);
    }
}
