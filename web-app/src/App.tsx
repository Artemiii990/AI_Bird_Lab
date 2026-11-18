import { useState, useEffect, useRef } from 'react';
import type { BirdRecord, StatItem } from './types/bird';
import { SUBSCRIPTION_PRICE_ETH } from './config/constants';
import { birdApi } from './services/api';
import { web3Service } from './services/web3';
import { styles as s } from './styles/appStyles';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<BirdRecord | null>(null);
  const [history, setHistory] = useState<BirdRecord[]>([]);
  const [stats, setStats] = useState<StatItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const [wallet, setWallet] = useState<string | null>(null);
  const [subscribed, setSubscribed] = useState(false);
  const [txPending, setTxPending] = useState(false);

  const inputRef = useRef<HTMLInputElement | null>(null);

  const loadData = async (query = '') => {
    try {
      const [historyData, statsData] = await Promise.all([
        birdApi.getHistory(query),
        birdApi.getStats(),
      ]);
      setHistory(historyData);
      setStats(statsData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleConnect = async () => {
    try {
      const { address, isSubscribed } = await web3Service.connectAndCheck();
      setWallet(address);
      setSubscribed(isSubscribed);
    } catch (err: any) {
      alert(err.message || 'Не вдалося підключити гаманець');
    }
  };

  const handleSubscribe = async () => {
    setTxPending(true);
    try {
      await web3Service.purchaseSubscription();
      setSubscribed(true);
    } catch {
      alert('Транзакцію скасовано або недостатньо коштів');
    } finally {
      setTxPending(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file || !subscribed) return;
    setLoading(true);
    try {
      const record = await birdApi.analyzeBird(file);
      setResult(record);
      loadData(search);
    } catch {
      alert('Помилка з’єднання з сервером');
    } finally {
      setLoading(false);
    }
  };

  const onFileChange = (selected: File | null) => {
    if (!selected) return;
    setFile(selected);
    setResult(null);
    setPreview(URL.createObjectURL(selected));
  };

  const totalScans = stats.reduce((sum, item) => sum + item.count, 0);

  return (
    <div style={s.page}>
      <div style={s.container}>
        <header style={s.header}>
          <div>
            <h1 style={s.title}>🦅 AI Bird Vision Lab</h1>
            <p style={s.subtitle}>Нейромережева класифікація птахів із Web3-підпискою</p>
          </div>

          {!wallet ? (
            <button onClick={handleConnect} style={s.walletBtn}>
              🦊 Підключити гаманець
            </button>
          ) : (
            <div style={s.walletBadge}>
              <span style={{ ...s.dot, background: subscribed ? '#10b981' : '#f59e0b' }} />
              {wallet.slice(0, 6)}...{wallet.slice(-4)} • {subscribed ? 'PRO Активна' : 'Без підписки'}
            </div>
          )}
        </header>

        <div style={s.grid}>
          <section style={s.card}>
            <h2 style={s.cardTitle}>01. Сканер зображень</h2>

            <div style={s.dropzone} onClick={() => inputRef.current?.click()}>
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => onFileChange(e.target.files?.[0] || null)}
              />
              {preview ? (
                <img src={preview} alt="Preview" style={s.previewImg} />
              ) : (
                <p style={s.dropText}>📸 Натисніть, щоб вибрати фото птаха</p>
              )}
            </div>

            {!wallet && (
              <button onClick={handleConnect} style={s.primaryBtn}>
                🦊 Підключіть MetaMask для доступу
              </button>
            )}

            {wallet && !subscribed && (
              <button onClick={handleSubscribe} disabled={txPending} style={s.payBtn}>
                {txPending
                  ? '⏳ Підтвердження транзакції...'
                  : `💎 Купити підписку (${SUBSCRIPTION_PRICE_ETH} ETH / 30 днів)`}
              </button>
            )}

            {wallet && subscribed && (
              <button onClick={handleAnalyze} disabled={!file || loading} style={s.primaryBtn}>
                {loading ? '⚡ Аналіз...' : '✨ Розпізнати вид птаха'}
              </button>
            )}

            {result && (
              <div style={s.resultBox}>
                <div style={s.resultHeader}>
                  <strong>{result.species.toUpperCase()}</strong>
                  <span style={s.badge}>{result.confidence}%</span>
                </div>
                <p style={s.resultDesc}>{result.description}</p>
              </div>
            )}
          </section>

          <section style={s.card}>
            <h2 style={s.cardTitle}>02. Аналітика популяції</h2>

            <div style={s.kpiRow}>
              <div style={s.kpiBox}>
                <span style={s.kpiVal}>{totalScans}</span>
                <span style={s.kpiLbl}>Всього сканувань</span>
              </div>
              <div style={s.kpiBox}>
                <span style={s.kpiVal}>{stats.length}</span>
                <span style={s.kpiLbl}>Унікальних видів</span>
              </div>
            </div>

            <div style={s.statsList}>
              {stats.length === 0 ? (
                <p style={s.muted}>Даних поки немає</p>
              ) : (
                stats.map((item) => {
                  const pct = totalScans ? Math.round((item.count / totalScans) * 100) : 0;
                  return (
                    <div key={item.species}>
                      <div style={s.statTop}>
                        <span>{item.species}</span>
                        <span style={s.muted}>{item.count} ({pct}%)</span>
                      </div>
                      <div style={s.barBg}>
                        <div style={{ ...s.barFill, width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </section>
        </div>

        <section style={{ ...s.card, marginTop: 24 }}>
          <div style={s.historyTop}>
            <h2 style={s.cardTitle}>03. Історія спостережень (MS SQL)</h2>
            <input
              type="text"
              placeholder="🔍 Пошук за видом..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                loadData(e.target.value);
              }}
              style={s.searchInput}
            />
          </div>

          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>ID</th>
                <th style={s.th}>Файл</th>
                <th style={s.th}>Вид</th>
                <th style={s.th}>Точність</th>
                <th style={s.th}>Деталі</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.id} style={s.tr}>
                  <td style={s.td}>#{row.id}</td>
                  <td style={s.td}>{row.fileName}</td>
                  <td style={s.td}><span style={s.tag}>{row.species}</span></td>
                  <td style={s.td}>{row.confidence}%</td>
                  <td style={{ ...s.td, color: '#94a3b8' }}>{row.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}