import { API_URL } from '../config/constants';
import type { BirdRecord, StatItem } from '../types/bird';

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_FILE_SIZE_MB = 10;

export const birdApi = {
  async getHistory(search = ''): Promise<BirdRecord[]> {
    const res = await fetch(`${API_URL}/history?search=${encodeURIComponent(search)}`);
    if (!res.ok) throw new Error('Не вдалося завантажити історію');
    return res.json();
  },

  async getStats(): Promise<StatItem[]> {
    const res = await fetch(`${API_URL}/stats`);
    if (!res.ok) throw new Error('Не вдалося завантажити статистику');
    return res.json();
  },

  async analyzeBird(file: File): Promise<BirdRecord> {
    if (!ALLOWED_TYPES.includes(file.type)) {
      throw new Error('Недопустимий формат файлу. Дозволені лише JPG, PNG або WEBP.');
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      throw new Error(`Розмір файлу не повинен перевищувати ${MAX_FILE_SIZE_MB} МБ.`);
    }

    const formData = new FormData();
    formData.append('file', file);

    let res: Response;
    try {
      res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });
    } catch {
      throw new Error('Помилка з’єднання з сервером');
    }

    if (!res.ok) {
      const errorData = await res.json().catch(() => null);
      throw new Error(errorData?.detail || 'Недопустимий формат файлу або на фото немає птаха.');
    }

    return res.json();
  },
};