export interface BirdRecord {
  id: number;
  fileName: string;
  species: string;
  confidence: number;
  description: string;
  date?: string;
}

export interface StatItem {
  species: string;
  count: number;
}