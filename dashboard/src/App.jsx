import React, { useState, useEffect, useRef } from 'react';
import {
  Menu, X, Plus, Send, MessageSquare, Shield,
  Settings, User, Zap, Activity, Battery,
  Cpu, Bell, ChevronLeft, Brain, Smartphone, ImagePlus, Save
} from 'lucide-react';
import { db } from './lib/firebase';
import { doc, onSnapshot, collection, query, orderBy, limit, setDoc } from 'firebase/firestore';

// 🎨 Theme Constants
const THEME = {
  bg: '#0F172A',
  sidebar: '#0B1224',
  primary: '#2AABEE',
  success: '#00FA9A',
  alert: '#FF4B4B',
};

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [status, setStatus] = useState({ battery: 0, last_seen: null });
  const [logs, setLogs] = useState([]);
  const [history, setHistory] = useState([
    { id: 1, title: 'Analyze Screen', date: '2 hours ago' },
  ]);
  const [isProcessing, setProcessing] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const fileInputRef = useRef(null);

  // --- CONFIG STATE (New System) ---
  const [deviceId, setDeviceId] = useState(localStorage.getItem('phage_device_id') || 'kigali_node_01');
  const [telegramToken, setTelegramToken] = useState(localStorage.getItem('phage_tg_token') || '');

  useEffect(() => {
    // Poll status based on CURRENT device id
    const unsubStatus = onSnapshot(doc(db, 'status', deviceId), (doc) => {
      if (doc.exists()) setStatus(doc.data());
    });

    const unsubLogs = onSnapshot(query(collection(db, 'logs'), orderBy('timestamp', 'desc'), limit(50)), (snap) => {
      setLogs(snap.docs.map(d => ({ id: d.id, ...d.data() })));
    });

    return () => { unsubStatus(); unsubLogs(); };
  }, [deviceId]);

  const saveSettings = async () => {
    localStorage.setItem('phage_device_id', deviceId);
    localStorage.setItem('phage_tg_token', telegramToken);

    // Bind token to user on Brain
    if (telegramToken) {
      await setDoc(doc(db, 'users', 'web_dashboard'), { telegram_token: telegramToken }, { merge: true });
    }
    alert("🧬 Protocol Updated: Settings Saved.");
    setActiveTab('chat');
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim() && !imageFile) return;

    setProcessing(true);
    const BRAIN_URL = "https://phage-gatway-343327310617.europe-west1.run.app";
    try {
      if (imageFile) {
        const fd = new FormData();
        fd.append('image', imageFile);
        fd.append('device_id', deviceId);
        fd.append('chat_id', 'web_dashboard');
        fd.append('caption', userInput || 'Analyze and navigate.');
        await fetch(BRAIN_URL, { method: 'POST', body: fd });
        setImageFile(null);
      } else {
        await fetch(BRAIN_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: deviceId,
            message: { chat: { id: "web_dashboard" }, text: userInput }
          })
        });
      }
      setUserInput('');
    } catch (err) {
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-200 font-sans overflow-hidden">

      {/* 🟢 Sidebar */}
      <div className={`fixed inset-0 z-50 transition-all duration-300 md:relative md:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} w-full md:w-72 bg-slate-950 border-r border-white/5 flex flex-col`}>
        <div className="p-4 flex items-center justify-between border-b border-white/5">
          <div className="flex items-center space-x-2">
            <Brain className="text-brand-telegram" size={24} />
            <h1 className="text-xl font-bold tracking-tight">Phage<span className="text-brand-telegram">OS</span></h1>
          </div>
          <button className="md:hidden" onClick={() => setSidebarOpen(false)}><X size={24} /></button>
        </div>

        <div className="p-4">
          <button onClick={() => setActiveTab('chat')} className="w-full flex items-center justify-center space-x-2 bg-slate-800 p-4 rounded-2xl font-semibold"><Plus size={20} /><span>New Chat</span></button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <h3 className="text-[10px] font-bold text-slate-500 uppercase px-4">Management</h3>
          <nav className="space-y-1">
            <button onClick={() => setActiveTab('chat')} className={`w-full text-left px-4 py-3 rounded-xl flex items-center space-x-3 ${activeTab === 'chat' ? 'bg-brand-telegram/10 text-brand-telegram' : 'hover:bg-white/5'}`}><MessageSquare size={18} /><span>Chat</span></button>
            <button onClick={() => setActiveTab('settings')} className={`w-full text-left px-4 py-3 rounded-xl flex items-center space-x-3 ${activeTab === 'settings' ? 'bg-brand-telegram/10 text-brand-telegram' : 'hover:bg-white/5'}`}><Settings size={18} /><span>Protocol Setup</span></button>
          </nav>
        </div>

        <div className="p-4 border-t border-white/5">
          <div className="bg-slate-900/50 p-4 rounded-2xl flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-brand-telegram/20 flex items-center justify-center"><Smartphone size={16} /></div>
            <div className="min-w-0"><p className="text-xs font-bold truncate">{deviceId}</p><p className="text-[10px] text-brand-symbiote uppercase font-black">Active</p></div>
          </div>
        </div>
      </div>

      {/* 🚀 Main */}
      <div className="flex-1 flex flex-col min-w-0">

        <main className="flex-1 overflow-y-auto custom-scrollbar">

          {activeTab === 'chat' && (
            <div className="max-w-3xl mx-auto p-4 md:p-8 space-y-8">
              <div className="flex justify-center space-x-2">
                <div className="bg-slate-900 px-3 py-1 rounded-full flex items-center space-x-2"><Battery size={12} /><span className="text-[10px] font-bold">{status.battery}%</span></div>
                <div className="bg-slate-900 px-3 py-1 rounded-full flex items-center space-x-2"><Activity size={12} /><span className="text-[10px] font-bold">Online</span></div>
              </div>

              <div className="space-y-12">
                <div className="flex space-x-4">
                  <div className="w-10 h-10 rounded-full bg-brand-telegram/10 flex items-center justify-center border border-brand-telegram/20"><Brain className="text-brand-telegram" size={20} /></div>
                  <div className="space-y-2">
                    <h2 className="text-3xl font-medium">Identify Protocol.</h2>
                    <p className="text-slate-400">I am connected to <b>{deviceId}</b>. Give me an instruction.</p>
                  </div>
                </div>
                {logs.slice(0, 10).map(log => (
                  <div key={log.id} className="flex space-x-4 border-l border-slate-800 pl-4 py-1 opacity-60"><div className="text-[10px] font-bold uppercase text-slate-500 pt-1">Sync</div><div className="text-sm text-slate-400">{log.message}</div></div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="max-w-2xl mx-auto p-4 md:p-12 space-y-8">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold">Muscle Preparation</h1>
                <p className="text-slate-500">Configure your device node and Telegram bot.</p>
              </div>

              <div className="space-y-6">
                <div className="space-y-3">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Node Identifier (DEVICE_ID)</label>
                  <input
                    value={deviceId}
                    onChange={(e) => setDeviceId(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 p-4 rounded-2xl outline-none focus:border-brand-telegram"
                    placeholder="e.g. node_kigali_01"
                  />
                  <p className="text-[10px] text-slate-600">This must match the DEVICE_ID in your phage.sh script.</p>
                </div>

                <div className="space-y-3">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Telegram Bot Token</label>
                  <input
                    type="password"
                    value={telegramToken}
                    onChange={(e) => setTelegramToken(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 p-4 rounded-2xl outline-none focus:border-brand-telegram"
                    placeholder="Enter your BotFather token"
                  />
                  <p className="text-[10px] text-slate-600">Phage will use this token to reply to you on Telegram.</p>
                </div>

                <button
                  onClick={saveSettings}
                  className="w-full bg-brand-telegram text-white p-4 rounded-2xl font-bold flex items-center justify-center space-x-2"
                >
                  <Save size={20} />
                  <span>Save Protocol Settings</span>
                </button>
              </div>
            </div>
          )}
        </main>

        {activeTab === 'chat' && (
          <div className="p-4 md:p-8 bg-slate-950/80 backdrop-blur-xl border-t border-white/5">
            <div className="max-w-3xl mx-auto">
              <form onSubmit={handleSendMessage} className="relative">
                <input ref={fileInputRef} type="file" className="hidden" onChange={e => setImageFile(e.target.files[0])} />
                <div className="bg-slate-900 border border-white/10 rounded-[2rem] px-6 py-4 flex flex-col">
                  <textarea
                    rows="1"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Enter instruction..."
                    className="bg-transparent border-none outline-none text-lg resize-none"
                  />
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
                    <button type="button" onClick={() => fileInputRef.current?.click()} className="text-slate-500 hover:text-brand-telegram"><ImagePlus size={20} /></button>
                    <button type="submit" disabled={isProcessing} className="text-brand-telegram"><Send size={24} /></button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
