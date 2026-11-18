import { BrowserProvider, Contract, parseEther } from 'ethers';
import { CONTRACT_ABI, CONTRACT_ADDRESS, SUBSCRIPTION_PRICE_ETH } from '../config/constants';

const getEthereum = () => {
  const eth = (window as unknown as { ethereum?: any }).ethereum;
  if (!eth) throw new Error('Встановіть MetaMask у браузер');
  return eth;
};

export const web3Service = {
  async connectAndCheck(): Promise<{ address: string; isSubscribed: boolean }> {
    const provider = new BrowserProvider(getEthereum());
    const signer = await provider.getSigner();
    const address = await signer.getAddress();

    const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
    const isSubscribed: boolean = await contract.isSubscribed(address);

    return { address, isSubscribed };
  },

  async purchaseSubscription(): Promise<void> {
    const provider = new BrowserProvider(getEthereum());
    const signer = await provider.getSigner();
    const contract = new Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

    const tx = await contract.subscribe({ value: parseEther(SUBSCRIPTION_PRICE_ETH) });
    await tx.wait();
  },
};