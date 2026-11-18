export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/birds';

export const CONTRACT_ADDRESS =
  import.meta.env.VITE_CONTRACT_ADDRESS ||'0x5FbDB2315678afecb367f032d93F642f64180aa3';

export const SUBSCRIPTION_PRICE_ETH = '0.001';

export const CONTRACT_ABI = [
  'function subscribe() external payable',
  'function isSubscribed(address user) external view returns (bool)',
];