"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ImageIcon, 
  FileText, 
  Calendar, 
  ChevronRight, 
  Activity, 
  Clock,
  ArrowLeft,
  Search,
  Filter,
  Trash2
} from "lucide-react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";

interface AnalysisRecord {
  id: number;
  created_at: string;
  analysis_summary: {
    severity: string;
    lesion_count: number;
  };
  thumbnail: string;
}

export default function HistoryPage() {
  const searchParams = useSearchParams();
  const initialView = searchParams.get("view") || "photos";
  
  const [view, setView] = useState(initialView);
  const [records, setRecords] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      const phone = localStorage.getItem("userPhone");
      console.log("[History] Fetching for phone:", phone);
      
      if (!phone) {
        setError("User not logged in");
        setLoading(false);
        return;
      }

      try {
        const url = `http://localhost:8000/api/user/analyses/${phone}`;
        console.log("[History] Fetching URL:", url);
        
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        
        const data = await res.json();
        console.log("[History] Received records:", data.length);
        setRecords(data);
      } catch (err: any) {
        console.error("[History] Fetch error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  // Update view if URL changes
  useEffect(() => {
    const v = searchParams.get("view");
    if (v) setView(v);
  }, [searchParams]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to permanently delete this analysis? This action cannot be undone.")) {
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/api/user/analysis/${id}`, {
        method: 'DELETE',
      });

      if (!res.ok) throw new Error('Failed to delete');

      // Update local state
      setRecords(prev => prev.filter(r => r.id !== id));
    } catch (err: any) {
      alert("Error deleting record: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-4 border-[#004d40] border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50 font-['Plus_Jakarta_Sans',_sans-serif]">
      <Navbar />
      
      <main className="pt-32 pb-20 px-16 max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
            <Link 
              href="/analysis" 
              className="flex items-center gap-2 text-stone-400 hover:text-[#004d40] transition-colors mb-4 text-sm font-bold group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              Back to Analysis
            </Link>
            <h1 className="text-4xl font-black text-[#004d40] tracking-tight mb-2">
              Skin Journey History
            </h1>
            <p className="text-stone-500 font-medium max-w-xl">
              Track your skin's transformation over time. Access all your past scans and clinical reports in one secure place.
            </p>
          </div>

          <div className="flex bg-white p-1.5 rounded-2xl border border-stone-100 shadow-sm self-start">
            <button
              onClick={() => setView("photos")}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${
                view === "photos" 
                ? "bg-[#004d40] text-white shadow-lg shadow-[#004d40]/20" 
                : "text-stone-400 hover:text-stone-600"
              }`}
            >
              <ImageIcon className="w-4 h-4" />
              My Photos
            </button>
            <button
              onClick={() => setView("reports")}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all ${
                view === "reports" 
                ? "bg-[#004d40] text-white shadow-lg shadow-[#004d40]/20" 
                : "text-stone-400 hover:text-stone-600"
              }`}
            >
              <FileText className="w-4 h-4" />
              Report History
            </button>
          </div>
        </div>

        {error ? (
          <div className="bg-rose-50 border border-rose-100 p-8 rounded-3xl text-center">
            <p className="text-rose-600 font-bold">{error}</p>
          </div>
        ) : records.length === 0 ? (
          <div className="bg-white border border-stone-100 p-20 rounded-[2.5rem] text-center shadow-sm">
            <div className="w-20 h-20 bg-stone-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <Activity className="w-10 h-10 text-stone-200" />
            </div>
            <h3 className="text-2xl font-black text-stone-700 mb-2">No Records Yet</h3>
            <p className="text-stone-400 font-medium mb-8">Start your first skin analysis to see your journey here.</p>
            <Link 
              href="/analysis"
              className="inline-flex items-center gap-2 bg-[#004d40] text-white px-8 py-4 rounded-2xl font-bold hover:scale-105 transition-all shadow-xl shadow-[#004d40]/20"
            >
              Start New Analysis
            </Link>
          </div>
        ) : (
          <AnimatePresence mode="wait">
            {view === "photos" ? (
              <motion.div
                key="photos"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
              >
                {records.map((record, idx) => (
                  <motion.div
                    key={record.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="group bg-white rounded-3xl border border-stone-100 p-4 shadow-sm hover:shadow-xl hover:shadow-stone-200/50 transition-all cursor-pointer"
                  >
                    <div className="relative aspect-[4/5] rounded-[1.5rem] overflow-hidden mb-4 bg-stone-50">
                      <img 
                        src={`data:image/jpeg;base64,${record.thumbnail}`} 
                        alt="Skin analysis"
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                      />
                      <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-full text-[10px] font-black text-[#004d40] uppercase tracking-wider">
                        {record.analysis_summary.severity} Status
                      </div>
                    </div>
                    <div className="flex items-center justify-between px-1">
                      <div>
                        <div className="flex items-center gap-1.5 text-stone-400 mb-1">
                          <Calendar className="w-3 h-3" />
                          <span className="text-[10px] font-bold uppercase tracking-widest leading-none">
                            {new Date(record.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm font-black text-[#004d40]">
                          {record.analysis_summary.lesion_count} Markers Detected
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(record.id);
                          }}
                          className="w-8 h-8 rounded-full bg-rose-50 flex items-center justify-center text-rose-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm"
                          title="Delete Analysis"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                        <Link 
                          href={`/analysis/report?id=${record.id}`}
                          className="w-8 h-8 rounded-full bg-stone-50 flex items-center justify-center text-[#004d40] hover:bg-[#004d40] hover:text-white transition-all transition-all"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <motion.div
                key="reports"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                {records.map((record, idx) => (
                  <motion.div
                    key={record.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center bg-white rounded-3xl border border-stone-100 p-6 shadow-sm hover:shadow-xl hover:shadow-stone-200/50 transition-all"
                  >
                    <div className="w-14 h-14 rounded-2xl bg-[#004d40]/5 flex items-center justify-center text-[#004d40] mr-6">
                      <FileText className="w-6 h-6" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 text-[#004d40] mb-1">
                        <Calendar className="w-4 h-4" />
                        <span className="text-sm font-bold">
                          {new Date(record.created_at).toLocaleDateString()}
                        </span>
                        <span className="text-stone-300 mx-2">•</span>
                        <Clock className="w-4 h-4 text-stone-400" />
                        <span className="text-sm text-stone-500 font-medium">
                          {new Date(record.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <h4 className="text-lg font-black text-[#004d40]">
                        Clinical Screening Report #{record.id}
                      </h4>
                    </div>

                    <div className="flex items-center gap-12 mr-12 px-6 border-x border-stone-100">
                      <div className="text-center">
                        <span className="block text-[10px] font-black text-stone-300 uppercase tracking-widest mb-1">Severity</span>
                        <span className={`text-sm font-black px-3 py-1 rounded-full ${
                          record.analysis_summary.severity === 'Severe' 
                          ? 'bg-rose-50 text-rose-500' 
                          : record.analysis_summary.severity === 'Moderate'
                          ? 'bg-amber-50 text-amber-500'
                          : 'bg-emerald-50 text-emerald-500'
                        }`}>
                          {record.analysis_summary.severity}
                        </span>
                      </div>
                      <div className="text-center">
                        <span className="block text-[10px] font-black text-stone-300 uppercase tracking-widest mb-1">Lesions</span>
                        <span className="text-sm font-black text-stone-600">{record.analysis_summary.lesion_count} Detected</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <button 
                        onClick={() => handleDelete(record.id)}
                        className="w-10 h-10 rounded-2xl bg-rose-50 flex items-center justify-center text-rose-500 hover:bg-rose-500 hover:text-white transition-all"
                        title="Delete Analysis"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <Link 
                        href={`/analysis/report?id=${record.id}`}
                        className="bg-stone-50 hover:bg-[#004d40] text-stone-400 hover:text-white px-6 py-3 rounded-2xl text-xs font-black uppercase tracking-widest transition-all transition-all"
                      >
                        View Report
                      </Link>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </main>
    </div>
  );
}
