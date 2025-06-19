import { useState, useEffect } from 'react';
import { convertName, saveHistory, deleteHistory as deleteHistoryApi } from './api.js';
import './App.css';

// 간단한 로마자 표기 매핑 (임시)
const romanizationMap = {
    하린: 'Ha-rin',
    지훈: 'Ji-hun',
    민준: 'Min-jun',
    서연: 'Seo-yeon',
    현우: 'Hyun-woo',
    지민: 'Ji-min',
    수민: 'Su-min',
    다은: 'Da-eun',
    예준: 'Ye-jun',
    가은: 'Ga-eun',
    지아: 'Ji-a',
    윤우: 'Yoon-woo',
    시은: 'Si-eun',
};

export default function App() {
    const [name, setName] = useState('');
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);

    // 저장된 이름 목록
    const [savedList, setSavedList] = useState([]);

    // 현재 뷰: home | saved
    const [view, setView] = useState('home');

    // 초기 로컬스토리지 로드
    useEffect(() => {
        try {
            const raw = localStorage.getItem('savedNames');
            if (raw) {
                setSavedList(JSON.parse(raw));
            }
        } catch (_) {
            // ignore
        }
    }, []);

    const syncLocal = (list) => {
        try {
            localStorage.setItem('savedNames', JSON.stringify(list));
        } catch (_) {
            // ignore
        }
    };

    // 이름 유효성 검증 함수
    const validateName = (value) => {
        if (!value.trim()) return '이름을 입력해 주세요.';
        if (value.length > 30) return '30자 이내로 입력해 주세요.';
        if (!/^[A-Za-z ]+$/.test(value)) return '영문 대소문자와 공백만 사용할 수 있습니다.';
        return '';
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const validationMsg = validateName(name);
        if (validationMsg) {
            setError(validationMsg);
            return;
        }
        setLoading(true);
        setError('');
        try {
            const arr = await convertName(name);
            setCandidates(arr);
            setSelectedIndex(0);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // 입력 실시간 검증
    const handleChange = (e) => {
        const value = e.target.value;
        setName(value);
        setError(validateName(value));
    };

    // 후보 클릭 시 선택 변경
    const handleSelect = (idx) => {
        setSelectedIndex(idx);
    };

    // 발음 재생 (SpeechSynthesis 사용)
    const playPronunciation = (text) => {
        if (!window.speechSynthesis) return;
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = 'ko-KR';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
    };

    // 추천 이름 저장
    const saveCurrent = async () => {
        if (candidates.length === 0) return;
        const current = candidates[selectedIndex];
        const normName = name.trim().toLowerCase();
        const duplicate = savedList.find(
            (s) => s.koreanName === current.koreanName && s.englishName.toLowerCase() === normName
        );
        if (duplicate) {
            alert('이미 저장된 이름입니다.');
            return;
        }
        const newItem = {
            englishName: name,
            ...current,
            savedAt: new Date().toISOString(),
        };
        const newList = [newItem, ...savedList];
        setSavedList(newList);
        syncLocal(newList);

        saveHistory(name, current.koreanName);
    };

    const deleteSaved = (idx) => {
        const item = savedList[idx];
        const newList = savedList.filter((_, i) => i !== idx);
        setSavedList(newList);
        syncLocal(newList);
        if (item && item.id) {
            deleteHistoryApi(item.id);
        }
    };

    return (
        <main style={{ maxWidth: 480, margin: '0 auto', padding: '2rem' }}>
            <nav className="nav">
                <button type="button" className={view === 'home' ? 'active' : ''} onClick={() => setView('home')}>
                    Name Recommendation
                </button>
                <button type="button" className={view === 'saved' ? 'active' : ''} onClick={() => setView('saved')}>
                    Saved my Korean names ({savedList.length})
                </button>
            </nav>
            {view === 'home' && (
                <>
                    <h1>나의 한국어 이름은?</h1>
                    <h1>What is your Korean name?</h1>
                    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
                        <label htmlFor="englishName" className="sr-only">
                            영어 이름
                        </label>
                        <input
                            id="englishName"
                            name="englishName"
                            type="text"
                            placeholder="Write your name in English..."
                            value={name}
                            onChange={handleChange}
                            maxLength={30}
                            required
                            pattern="[A-Za-z ]{1,30}"
                            aria-describedby="nameError"
                            autoFocus
                            style={{ flex: 1, padding: '0.5rem' }}
                        />
                        <button type="submit" disabled={loading || !!error || !name.trim()}>
                            {loading ? '로딩...' : 'Recommend'}
                        </button>
                    </form>
                    {error && (
                        <p id="nameError" style={{ color: 'red' }}>
                            {error}
                        </p>
                    )}
                    {candidates.length > 0 && (
                        <section className="result" role="region" aria-labelledby="primaryName">
                            <div className="primary">
                                <h2 id="primaryName">{candidates[selectedIndex].koreanName}</h2>
                                <p className="meaning">{candidates[selectedIndex].meaning}</p>
                                <p className="roman">{romanizationMap[candidates[selectedIndex].koreanName] || ''}</p>
                                <p className="score" aria-label="트렌드 점수">
                                    🔥 {candidates[selectedIndex].eraScore}
                                </p>
                                <button
                                    type="button"
                                    className="audio-btn"
                                    onClick={() => playPronunciation(candidates[selectedIndex].koreanName)}
                                >
                                    🔊 발음 듣기
                                </button>
                                <button type="button" className="save-btn" onClick={saveCurrent}>
                                    💾 저장
                                </button>
                            </div>
                            <ul className="others" aria-label="다른 추천 이름들">
                                {candidates.map((c, idx) => {
                                    if (idx === selectedIndex) return null;
                                    return (
                                        <li
                                            key={idx}
                                            className="other-item"
                                            role="button"
                                            tabIndex={0}
                                            onClick={() => handleSelect(idx)}
                                            onKeyPress={(e) => {
                                                if (e.key === 'Enter' || e.key === ' ') handleSelect(idx);
                                            }}
                                        >
                                            <span className="name">{c.koreanName}</span>
                                            <span className="meaning">{c.meaning}</span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </section>
                    )}
                </>
            )}
            {view === 'saved' && (
                <section className="saved-list" aria-label="저장된 이름 목록">
                    {savedList.length === 0 ? (
                        <p>저장된 이름이 없습니다.</p>
                    ) : (
                        <ul>
                            {savedList.map((item, idx) => (
                                <li key={idx} className="saved-item">
                                    <span className="name">{item.koreanName}</span>
                                    <span className="meaning">{item.meaning}</span>
                                    <button type="button" onClick={() => deleteSaved(idx)}>
                                        Delete(삭제)
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </section>
            )}
        </main>
    );
}
