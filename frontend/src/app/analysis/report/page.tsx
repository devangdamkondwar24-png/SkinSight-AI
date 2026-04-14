"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import { GravityButton } from "@/components/GravityButton";
import { AnalysisOverlay } from "@/components/AnalysisOverlay";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ChevronLeft, Layers, Map, Thermometer, ShieldAlert, CheckCircle, ChevronDown } from "lucide-react";

export default function ReportDashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [data, setData] = useState<any>(null);
  
  // Overlay states
  const [toggles, setToggles] = useState({
    lesions: true,
    darkSpots: true,
    zones: false,
    mesh: false,
    pigmentation: false,
    heatmap: false,
  });

  const [activeTab, setActiveTab] = useState<"analysis" | "progress">("analysis");
  const [activeTimelineBlock, setActiveTimelineBlock] = useState<number>(1);

  useEffect(() => {
    const phone = localStorage.getItem("userPhone");
    const analysisId = searchParams.get("id");

    if (!phone && !analysisId) {
      router.push("/analysis");
      return;
    }

    const fetchAnalysis = async () => {
      try {
        let url = "";
        if (analysisId) {
          console.log("[Report] Fetching by ID:", analysisId);
          url = `http://localhost:8000/api/user/analysis/${analysisId}`;
        } else {
          console.log("[Report] Fetching latest for phone:", phone);
          url = `http://localhost:8000/api/user/analysis/${phone}/latest`;
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error("No analysis data found");
        
        const result = await response.json();
        setData(result);
      } catch (e) {
        console.error(e);
        router.push("/analysis");
      }
    };

    fetchAnalysis();
  }, [router, searchParams]);

  if (!data) return null;

  const toggleOverlay = (key: keyof typeof toggles) => {
    // Special rule: heatmap can overlap with others, or be exclusive? We'll let them mix.
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const { analysis, recommendations } = data;

  return (
    <main className="min-h-screen bg-[#f8faf9] text-[#191c1c] overflow-x-hidden pb-20">
      <Navbar />

      <div className="pt-32 px-16 max-w-[1920px] mx-auto">
        <header className="mb-24">
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-6xl font-bold tracking-tight text-[#191c1c] mb-4"
          >
            Clinical Analysis
          </motion.h1>

        </header>

        <div className="grid grid-cols-12 gap-12">
            
          {/* Left Side: Visual Input & Core Metrics */}
          <section className="col-span-12 lg:col-span-8 space-y-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              {/* Patient Image View with Control Panel Overlay */}
              <div className="bg-white p-6 rounded-lg clinical-frame overflow-hidden flex flex-col shadow-[0_20px_50px_rgba(0,0,0,0.05)] border border-white/20">
                <div className="flex justify-between items-center mb-6">
                  <span className="text-[10px] font-bold tracking-[0.2em] text-[#4e635e] uppercase">Spectral Capture 001-A</span>
                  <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <div className="w-1.5 h-1.5 rounded-full bg-stone-200"></div>
                    <div className="w-1.5 h-1.5 rounded-full bg-stone-200"></div>
                  </div>
                </div>

                <div className="flex gap-6 grow">
                  {/* Main Image Overlay */}
                  <div className="relative flex-1 aspect-[3/4] rounded-sm overflow-hidden bg-stone-100">
                    <AnalysisOverlay 
                      data={data}
                      showLesions={toggles.lesions}
                      showDarkSpots={toggles.darkSpots}
                      showZones={toggles.zones}
                      showMesh={toggles.mesh}
                      showPigmentation={toggles.pigmentation}
                      showHeatmap={toggles.heatmap}
                    />
                    <div className="absolute bottom-4 left-4 right-4 bg-white/10 backdrop-blur-md border border-white/20 p-3 rounded text-[10px] text-white font-mono uppercase tracking-widest pointer-events-none">
                      Processing Neural Map... Active
                    </div>
                  </div>

                  {/* Analysis Control Panel (Sidebar style) */}
                  <div className="flex flex-col gap-2 w-36 shrink-0">
                    <div className="mb-4">
                      <p className="text-[9px] font-bold text-[#424846]/40 tracking-[0.2em] uppercase">Visual Layers</p>
                    </div>
                    {[
                      { id: 'lesions', label: 'Lesions' },
                      { id: 'darkSpots', label: 'Dark Spots' },
                      { id: 'zones', label: 'Zones' },
                      { id: 'heatmap', label: 'Heatmap' },
                      { id: 'mesh', label: 'Mesh' },
                      { id: 'pigmentation', label: 'Hyperpig.' },
                    ].map((btn) => (
                      <button 
                        key={btn.id}
                        onClick={() => toggleOverlay(btn.id as any)}
                        className={`text-[10px] font-bold py-3 px-4 rounded border transition-all text-left flex items-center justify-between group ${
                          toggles[btn.id as keyof typeof toggles] 
                          ? "bg-[#4e635e] text-white border-transparent shadow-lg" 
                          : "bg-stone-50 text-[#424846] border-stone-200 hover:border-[#4e635e]/40"
                        }`}
                      >
                        {btn.label}
                        {toggles[btn.id as keyof typeof toggles] && <span className="material-symbols-outlined text-[14px]">check</span>}
                      </button>
                    ))}

                  </div>
                </div>

              </div>

              {/* Clinical Severity Scale */}
              <div className="bg-white p-10 rounded-lg flex flex-col justify-center border border-white/20 shadow-[0_20px_50px_rgba(0,0,0,0.05)]">
                <div className="mb-10">
                  <span className="text-xs font-semibold tracking-widest text-[#4e635e] uppercase block mb-2">Primary Diagnosis</span>
                  <h2 className="text-3xl font-bold">Severity Scale</h2>
                </div>
                <div className="relative pt-8 pb-4">
                  {/* Dynamic Target Indicator Mapping */}
                  <div 
                    className="absolute -top-4 transition-all duration-1000 ease-out flex flex-col items-center"
                    style={{ left: `${analysis?.acne_severity?.score || 50}%`, transform: 'translateX(-50%)' }}
                  >
                    <span className="bg-[#4e635e] text-white text-[10px] font-bold px-2 py-0.5 rounded-full mb-1 whitespace-nowrap">
                      {analysis?.acne_severity?.grade || "Neutral"}
                    </span>
                    <div className="w-0.5 h-4 bg-[#4e635e]"></div>
                  </div>
                  <div className="h-3 w-full rounded-full bg-stone-100 flex overflow-hidden">
                    <div className="h-full w-1/4 bg-emerald-50"></div>
                    <div className="h-full w-1/4 bg-emerald-100"></div>
                    <div className="h-full w-1/4 bg-emerald-300"></div>
                    <div className="h-full w-1/4 bg-emerald-600"></div>
                  </div>
                  <div className="flex justify-between mt-4 text-[10px] font-bold text-[#424846] uppercase tracking-widest">
                    <span>Clear</span>
                    <span className="text-[#4e635e]">Moderate</span>
                    <span>Severe</span>
                  </div>
                </div>
                <div className="mt-12 bg-emerald-50/30 border border-emerald-500/10 p-4 rounded text-sm italic text-[#4e635e]">
                  "{analysis?.acne_severity?.description || "Current observation indicates localized markers with moderate epidermal stress indicator."}"
                </div>
              </div>
            </div>

            {/* Metrics and Action Plan Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-stone-50 p-12 rounded-lg group hover:bg-stone-100 transition-colors duration-300 border border-transparent hover:border-stone-200">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center">
                    <span className="material-symbols-outlined text-[#4e635e]" style={{ fontVariationSettings: "'FILL' 1" }}>biotech</span>
                  </div>
                  <h3 className="text-lg font-bold text-charcoal">Detection Metrics</h3>
                </div>
                <div className="space-y-8">
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-5xl font-extrabold text-[#191c1c] mb-1">
                        {analysis?.lesion_count_bucket || analysis?.acne_severity?.total_lesions || 0}
                      </p>
                      <p className="text-[#424846] font-medium">Lesion Load Profile</p>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-[#b400ff] mb-1">{analysis?.acne_severity?.dark_spot_count || 0}</p>
                      <p className="text-[#424846] text-xs font-semibold uppercase tracking-tighter">Dark Spots</p>
                    </div>
                  </div>
                  <div className="h-[1px] bg-stone-200/50"></div>
                  <div>
                    <p className="text-5xl font-extrabold text-[#191c1c] mb-1">{(analysis?.overall_redness || 15).toFixed(0)}%</p>
                    <p className="text-[#424846] font-medium">Surface Inconsistency</p>
                  </div>
                </div>
              </div>

              <div className="bg-stone-50 p-12 rounded-lg flex flex-col justify-between border-2 border-[#4e635e]/5">
                <div>
                  <span className="text-xs font-bold tracking-widest text-[#4e635e] uppercase block mb-6">Clinical Insight</span>
                  <h3 className="text-2xl font-bold text-charcoal mb-4 leading-snug">
                    {recommendations?.lifestyle_advice || "Personalized clinical intervention recommended based on active detection."}
                  </h3>
                </div>
                <button 
                  onClick={() => router.push('/treatments')}
                  className="bg-[#4e635e] text-white w-full py-5 rounded px-8 font-bold text-sm tracking-widest uppercase transition-all flex justify-between items-center group shadow-xl shadow-[#4e635e]/10 active:scale-95"
                >
                  Generate Full Protocol
                  <span className="material-symbols-outlined group-hover:translate-x-2 transition-transform">arrow_forward</span>
                </button>
              </div>
            </div>


          </section>

          {/* Right Side: Secondary Analysis Dashboard */}
          <section className="col-span-12 lg:col-span-4 space-y-8">
            <div className="bg-white p-10 rounded-lg border border-white/20 shadow-[0_20px_50px_rgba(0,0,0,0.05)]">
              <h3 className="text-xl font-bold mb-10 tracking-tight text-charcoal">Zone Health Status</h3>
              <div className="space-y-8 max-h-[500px] overflow-y-auto pr-4 custom-scrollbar">
                {Object.entries(analysis?.zone_health || {}).map(([zone, info]: any) => {
                  // Standardized score mapping
                  const score = info.severity === 'clear' ? 85 : info.severity === 'mild' ? 62 : 41;
                  const barColor = info.severity === 'clear' ? 'bg-emerald-500' : info.severity === 'mild' ? 'bg-orange-400' : 'bg-red-500';
                  const textColor = info.severity === 'clear' ? 'text-emerald-700' : info.severity === 'mild' ? 'text-orange-700' : 'text-red-700';
                  
                  return (
                    <div key={zone} className="group">
                      <div className="flex justify-between items-end mb-2">
                        <span className="text-[11px] font-black uppercase tracking-widest text-[#191c1c]">{info.display_name || zone.replace(/_/g, ' ')}</span>
                        <span className={`text-[10px] font-black tracking-tighter ${textColor} px-2 py-0.5 bg-stone-50 rounded`}>
                           {score}% {info.severity.toUpperCase()}
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-stone-100 rounded-full overflow-hidden border border-stone-200/50">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${score}%` }}
                          transition={{ duration: 1.2, ease: "circOut" }}
                          className={`h-full ${barColor}`} 
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-16 p-6 rounded bg-stone-50 border-l-4 border-[#4e635e]/20">
                <div className="flex gap-4 text-charcoal">
                  <span className="material-symbols-outlined text-[#4e635e]">info</span>
                  <p className="text-sm text-[#424846] leading-relaxed italic">
                    {recommendations?.pm_routine?.[0]?.detail || "The identified zones show varying degrees of epidermal pressure. Prioritize high-concern areas in tonight's routine."}
                  </p>
                </div>
              </div>
            </div>


          </section>
        </div>
      </div>
      
      <footer className="w-full py-24 px-16 mt-32 bg-stone-100 border-t border-stone-200">
        <div className="flex flex-col md:flex-row justify-between items-start w-full max-w-[1920px] mx-auto text-sm leading-relaxed text-[#424846]">
          <div className="mb-12 md:mb-0">
            <div className="text-lg font-bold text-[#4e635e] mb-4 uppercase tracking-[0.05em]">SkinSight</div>
            <p className="max-w-xs text-[#727876] font-medium leading-relaxed">
              © 2026 SkinSight. Clinical Precision in Skincare. Utilizing state-of-the-art dermatological analysis.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-16">
            <div className="flex flex-col space-y-4">
              <span className="font-black text-[#4e635e] uppercase tracking-widest text-[10px]">Platform</span>
              <a className="hover:text-[#4e635e] transition-colors font-bold" href="#">Privacy Policy</a>
              <a className="hover:text-[#4e635e] transition-colors font-bold" href="#">Terms of Service</a>
            </div>
            <div className="flex flex-col space-y-4">
              <span className="font-black text-[#4e635e] uppercase tracking-widest text-[10px]">Resources</span>
              <a className="hover:text-[#4e635e] transition-colors font-bold" href="#">Clinical Methodology</a>
              <a className="hover:text-[#4e635e] transition-colors font-bold" href="#">Contact Support</a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}

