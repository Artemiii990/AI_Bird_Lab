import { useState, useEffect, useRef } from 'react';

interface BirdRecord {
  id: number;
  fileName: string;
  species: string;
  confidence: number;
  description: string;
  date: string;
}

interface StatItem {
  species: string;
  count: number;
}

const API_URL = 'http://localhost:5000/api/birds';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<BirdRecord | null>(null);
  const [history, setHistory] = useState<BirdRecord[]>([]);
  const [stats, setStats] = useState<StatItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadData = async (query = '') => {
    try {
      const [histRes, statRes] = await Promise.all([
        fetch(`${API_URL}/history?search=${query}`),
        fetch(`${API_URL}/stats`)
      ]);
      setHistory(await histRes.json());
      setStats(await statRes.json());
    } catch (err) {
      console.error('API Error:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileSelect = (selectedFile: File | null) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setResult(null);
    setPreviewUrl(URL.createObjectURL(selectedFile));
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/analyze`, { method: 'POST', body: formData });
      const data = await res.json();
      setResult(data);
      loadData(search);
    } catch {
      alert('Помилка з’єднання з сервером. Перевірте Docker-контейнери.');
    } finally {
      setLoading(false);
    }
  };

  const totalScans = stats.reduce((acc, item) => acc + item.count, 0);

  return (
    <div style={styles.page}>
      {/* Фоновое свечение */}
      <div style={styles.glowTop} />
      <div style={styles.glowBottom} />

      <div style={styles.container}>
        {/* Шапка */}
        <header style={styles.header}>
          <div style={styles.logoGroup}>
            <div style={styles.logoIcon}>🦅</div>
            <div>
              <h1 style={styles.title}>
                AI Bird <span style={styles.gradientText}>Vision Lab</span>
              </h1>
              <p style={styles.subtitle}>Нейромережева система класифікації орнітофауни</p>
            </div>
          </div>

          <div style={styles.statusBadge}>
            <span style={styles.statusDot} />
            ResNet-50 Neural Engine Active
          </div>
        </header>

        {/* Верхняя сетка (Bento Grid): Сканер + Статистика */}
        <div style={styles.bentoGrid}>
          {/* Левая карточка: Загрузка и распознавание */}
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.stepBadge}>01</span>
              <h2 style={styles.cardTitle}>Сканер зображень</h2>
            </div>

            <div
              style={{
                ...styles.dropzone,
                borderColor: isDragging ? '#10b981' : 'rgba(255,255,255,0.12)',
                background: isDragging ? 'rgba(16, 185, 129, 0.08)' : 'rgba(15, 23, 42, 0.5)'
              }}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                handleFileSelect(e.dataTransfer.files?.[0] || null);
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
              />

              {previewUrl ? (
                <div style={styles.previewWrapper}>
                  <img src={previewUrl} alt="Preview" style={styles.previewImg} />
                  <div style={styles.previewOverlay}>Натисніть, щоб змінити фото</div>
                </div>
              ) : (
                <div style={styles.dropzoneContent}>
                  <div style={styles.uploadCircle}>📸</div>
                  <p style={styles.dropText}>Перетягніть фото птаха сюди або натисніть для вибору</p>
                  <span style={styles.dropHint}>Підтримуються JPG, PNG, WEBP</span>
                </div>
              )}
            </div>

            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              style={{
                ...styles.primaryBtn,
                opacity: !file || loading ? 0.5 : 1,
                cursor: !file || loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '⚡ Аналіз нейромережею...' : '✨ Розпізнати вид птаха'}
            </button>

            {/* Результат распознавания */}
            {result && (
              <div style={styles.resultBox}>
                <div style={styles.resultTop}>
                  <div>
                    <span style={styles.resultLabel}>Визначений вид</span>
                    <h3 style={styles.resultSpecies}>{result.species.toUpperCase()}</h3>
                  </div>
                  <div style={styles.confidencePill}>{result.confidence}% впевненості</div>
                </div>

                {/* Прогресс-бар уверенности */}
                <div style={styles.progressTrack}>
                  <div style={{ ...styles.progressFill, width: `${result.confidence}%` }} />
                </div>

                <p style={styles.resultDesc}>{result.description}</p>
              </div>
            )}
          </div>

          {/* Правая карточка: Аналитика и статистика */}
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.stepBadge}>02</span>
              <h2 style={styles.cardTitle}>Аналітика популяції</h2>
            </div>

            <div style={styles.kpiRow}>
              <div style={styles.kpiBox}>
                <span style={styles.kpiValue}>{totalScans}</span>
                <span style={styles.kpiLabel}>Всього сканувань</span>
              </div>
              <div style={styles.kpiBox}>
                <span style={styles.kpiValue}>{stats.length}</span>
                <span style={styles.kpiLabel}>Унікальних видів</span>
              </div>
            </div>

            <h3 style={styles.subSectionTitle}>Розподіл за видами</h3>
            {stats.length === 0 ? (
              <div style={styles.emptyState}>Завантажте перше фото, щоб побачити статистику</div>
            ) : (
              <div style={styles.statsList}>
                {stats.map((s) => {
                  const pct = totalScans > 0 ? Math.round((s.count / totalScans) * 100) : 0;
                  return (
                    <div key={s.species} style={styles.statItem}>
                      <div style={styles.statRowTop}>
                        <span style={styles.statName}>{s.species}</span>
                        <span style={styles.statCount}>{s.count} шт. ({pct}%)</span>
                      </div>
                      <div style={styles.statBarBg}>
                        <div style={{ ...styles.statBarFill, width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Нижняя карточка: Журнал (MS SQL History) */}
        <div style={{ ...styles.card, marginTop: 24 }}>
          <div style={styles.historyHeader}>
            <div style={styles.cardHeader}>
              <span style={styles.stepBadge}>03</span>
              <h2 style={styles.cardTitle}>База даних спостережень (MS SQL)</h2>
            </div>

            <div style={styles.searchWrapper}>
              <span>🔍</span>
              <input
                type="text"
                placeholder="Пошук за видом птаха..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  loadData(e.target.value);
                }}
                style={styles.searchInput}
              />
            </div>
          </div>

          {history.length === 0 ? (
            <div style={styles.emptyState}>Записів у базі даних поки не знайдено</div>
          ) : (
            <div style={styles.tableWrapper}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>ID</th>
                    <th style={styles.th}>Файл</th>
                    <th style={styles.th}>Вид птаха</th>
                    <th style={styles.th}>Точність AI</th>
                    <th style={styles.th}>Біологічна довідка</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id} style={styles.tr}>
                      <td style={styles.tdId}>#{item.id}</td>
                      <td style={styles.tdFile}>{item.fileName}</td>
                      <td style={styles.td}>
                        <span style={styles.speciesTag}>{item.species}</span>
                      </td>
                      <td style={styles.td}>
                        <span style={styles.confText}>{item.confidence}%</span>
                      </td>
                      <td style={styles.tdDesc}>{item.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    background: '#090d16',
    color: '#f8fafc',
    position: 'relative',
    overflow: 'hidden',
    padding: '32px 20px',
  },
  glowTop: {
    position: 'absolute',
    top: -150,
    left: '15%',
    width: 500,
    height: 500,
    background: 'radial-gradient(circle, rgba(16,185,129,0.15) 0%, rgba(0,0,0,0) 70%)',
    pointerEvents: 'none',
  },
  glowBottom: {
    position: 'absolute',
    bottom: -150,
    right: '10%',
    width: 600,
    height: 600,
    background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, rgba(0,0,0,0) 70%)',
    pointerEvents: 'none',
  },
  container: {
    maxWidth: 1120,
    margin: '0 auto',
    position: 'relative',
    zIndex: 1,
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 16,
    marginBottom: 32,
  },
  logoGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: 16,
  },
  logoIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 28,
    boxShadow: '0 10px 25px rgba(16, 185, 129, 0.3)',
  },
  title: {
    margin: 0,
    fontSize: 28,
    fontWeight: 800,
    letterSpacing: '-0.5px',
  },
  gradientText: {
    background: 'linear-gradient(90deg, #34d399, #38bdf8)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    margin: '4px 0 0',
    color: '#94a3b8',
    fontSize: 14,
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    padding: '8px 16px',
    borderRadius: 999,
    background: 'rgba(16, 185, 129, 0.1)',
    border: '1px solid rgba(16, 185, 129, 0.25)',
    color: '#34d399',
    fontSize: 13,
    fontWeight: 600,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#10b981',
    boxShadow: '0 0 10px #10b981',
  },
  bentoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
    gap: 24,
  },
  card: {
    background: 'rgba(17, 24, 39, 0.7)',
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: 20,
    padding: 24,
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 20,
  },
  stepBadge: {
    background: 'rgba(56, 189, 248, 0.15)',
    color: '#38bdf8',
    fontSize: 12,
    fontWeight: 700,
    padding: '4px 10px',
    borderRadius: 8,
  },
  cardTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 700,
  },
  dropzone: {
    border: '2px dashed rgba(255,255,255,0.12)',
    borderRadius: 16,
    minHeight: 200,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    overflow: 'hidden',
  },
  dropzoneContent: {
    textAlign: 'center',
    padding: 24,
  },
  uploadCircle: {
    width: 48,
    height: 48,
    borderRadius: '50%',
    background: 'rgba(255,255,255,0.06)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 22,
    margin: '0 auto 12px',
  },
  dropText: {
    margin: '0 0 6px',
    fontSize: 14,
    fontWeight: 500,
    color: '#e2e8f0',
  },
  dropHint: {
    fontSize: 12,
    color: '#64748b',
  },
  previewWrapper: {
    position: 'relative',
    width: '100%',
    height: 220,
  },
  previewImg: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  previewOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    background: 'rgba(9, 13, 22, 0.75)',
    color: '#e2e8f0',
    fontSize: 12,
    textAlign: 'center',
    padding: '8px 0',
  },
  primaryBtn: {
    width: '100%',
    marginTop: 16,
    padding: '14px 20px',
    borderRadius: 12,
    border: 'none',
    background: 'linear-gradient(135deg, #10b981 0%, #0284c7 100%)',
    color: '#fff',
    fontSize: 15,
    fontWeight: 700,
    boxShadow: '0 8px 20px rgba(16, 185, 129, 0.25)',
    transition: 'transform 0.15s ease',
  },
  resultBox: {
    marginTop: 20,
    padding: 18,
    borderRadius: 14,
    background: 'rgba(16, 185, 129, 0.08)',
    border: '1px solid rgba(16, 185, 129, 0.25)',
  },
  resultTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: 10,
  },
  resultLabel: {
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: '0.8px',
    color: '#34d399',
    fontWeight: 700,
  },
  resultSpecies: {
    margin: '4px 0 0',
    fontSize: 22,
    fontWeight: 800,
    color: '#fff',
  },
  confidencePill: {
    background: '#10b981',
    color: '#052e16',
    fontWeight: 800,
    fontSize: 12,
    padding: '5px 10px',
    borderRadius: 8,
  },
  progressTrack: {
    width: '100%',
    height: 6,
    background: 'rgba(255,255,255,0.1)',
    borderRadius: 999,
    margin: '12px 0',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #10b981, #38bdf8)',
    borderRadius: 999,
  },
  resultDesc: {
    margin: 0,
    fontSize: 14,
    color: '#cbd5e1',
    lineHeight: 1.5,
  },
  kpiRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 12,
    marginBottom: 24,
  },
  kpiBox: {
    background: 'rgba(15, 23, 42, 0.6)',
    border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: 14,
    padding: 16,
    display: 'flex',
    flexDirection: 'column',
  },
  kpiValue: {
    fontSize: 28,
    fontWeight: 800,
    color: '#f8fafc',
  },
  kpiLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  subSectionTitle: {
    fontSize: 13,
    textTransform: 'uppercase',
    letterSpacing: '0.6px',
    color: '#94a3b8',
    margin: '0 0 14px',
  },
  statsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
  },
  statItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  statRowTop: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 14,
  },
  statName: {
    fontWeight: 600,
    color: '#e2e8f0',
    textTransform: 'capitalize',
  },
  statCount: {
    color: '#94a3b8',
    fontSize: 13,
  },
  statBarBg: {
    width: '100%',
    height: 8,
    background: 'rgba(255,255,255,0.07)',
    borderRadius: 999,
    overflow: 'hidden',
  },
  statBarFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #38bdf8, #818cf8)',
    borderRadius: 999,
  },
  historyHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 16,
    marginBottom: 12,
  },
  searchWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: 'rgba(15, 23, 42, 0.8)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 12,
    padding: '8px 14px',
  },
  searchInput: {
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#f8fafc',
    fontSize: 14,
    width: 200,
  },
  tableWrapper: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    textAlign: 'left',
    padding: '12px 14px',
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    color: '#64748b',
    borderBottom: '1px solid rgba(255,255,255,0.08)',
  },
  tr: {
    borderBottom: '1px solid rgba(255,255,255,0.05)',
  },
  tdId: {
    padding: '14px',
    color: '#64748b',
    fontSize: 13,
    fontFamily: 'monospace',
  },
  tdFile: {
    padding: '14px',
    color: '#cbd5e1',
    fontSize: 14,
  },
  td: {
    padding: '14px',
  },
  speciesTag: {
    display: 'inline-block',
    padding: '4px 10px',
    borderRadius: 8,
    background: 'rgba(16, 185, 129, 0.15)',
    color: '#34d399',
    fontWeight: 700,
    fontSize: 13,
    textTransform: 'capitalize',
  },
  confText: {
    fontWeight: 700,
    color: '#38bdf8',
    fontSize: 14,
  },
  tdDesc: {
    padding: '14px',
    color: '#94a3b8',
    fontSize: 14,
  },
  emptyState: {
    padding: 32,
    textAlign: 'center',
    color: '#64748b',
    fontSize: 14,
    background: 'rgba(15, 23, 42, 0.4)',
    borderRadius: 12,
  },
};