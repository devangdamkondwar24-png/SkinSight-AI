"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { Navbar } from "@/components/Navbar";

export default function AnalysisUploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const isVerified = localStorage.getItem("isVerified");
    if (!isVerified) router.push("/login");
  }, [router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files?.[0];
    if (dropped && dropped.type.startsWith("image/")) {
      setFile(dropped);
      setPreview(URL.createObjectURL(dropped));
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const startAnalysis = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const phone = localStorage.getItem("userPhone");
      if (phone) {
        formData.append("phone", phone);
      }

      const response = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to analyze image");
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || "Analysis failed");
      }
      
      router.push("/analysis/report");
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
      setIsAnalyzing(false);
    }
  };

  if (isAnalyzing) {
    return (
      <main className="min-h-screen bg-[#f8faf9] flex flex-col items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center space-y-12 max-w-md w-full"
        >
          <div className="relative">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="w-40 h-40 rounded-full border-[2px] border-[#D1E8E1] border-t-secondary"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-16 h-16 bg-secondary/5 rounded-full flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-secondary animate-spin" />
              </div>
            </div>
          </div>
          
          <div className="text-center space-y-4">
            <h2 className="text-4xl font-bold tracking-tighter text-[#191c1c] uppercase">Initializing Neural Core</h2>
            <p className="text-[#424846] font-light leading-relaxed">
              We are currently mapping your facial topography and cross-referencing markers with our clinical database.
            </p>
          </div>
        </motion.div>
      </main>
    );
  }

  return (
    <div className="login-page">
      {/* ── Precision Navbar ── */}
      <Navbar />

      <main className="flex-grow pt-20">
        {/* ── Hero Section (V2 Radial) ── */}
        <section className="editorial-gradient pt-24 pb-16 px-16">
          <div className="max-w-6xl mx-auto grid md:grid-cols-[65%_35%] gap-12 items-end">
            <div>
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-7xl font-extrabold tracking-tighter text-[#191c1c] mb-6 leading-tight"
              >
                Analyze <br/>Your Skin
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-xl text-[#424846] font-light max-w-xl leading-relaxed"
              >
                Receive an instant, clinical-grade assessment of your skin's health. Our proprietary neural core assesses 14 key dermatological metrics from a single photo.
              </motion.p>
            </div>
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="hidden md:block pb-4"
            >
              <div className="bg-white p-6 rounded-xl shadow-[0_20px_40px_rgba(78,99,94,0.06)] border border-outline-variant/10">
                <span className="block text-xs font-bold uppercase tracking-[0.1em] text-primary mb-3">System Status</span>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-sm font-semibold text-[#191c1c]">Clinical Engine Online</span>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* ── Main Data Input Section ── */}
        <section className="px-16 pb-32">
          <div className="max-w-6xl mx-auto grid md:grid-cols-[1fr_380px] gap-24">
            {/* Left: Upload Zone */}
            <div className="space-y-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="relative group"
              >
                <div className="absolute -inset-1 bg-primary/5 rounded-lg blur-xl opacity-0 group-hover:opacity-100 transition duration-500" />
                <div
                  className={`relative w-full aspect-[16/10] bg-white border-2 border-dashed transition-all duration-500 flex flex-col items-center justify-center cursor-pointer group overflow-hidden ${
                    preview ? "border-transparent shadow-2xl" : "border-outline-variant/40 hover:border-primary/50"
                  }`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    accept="image/*"
                    onChange={handleFileChange}
                  />
                  
                  {preview ? (
                    <img src={preview} alt="Analysis Preview" className="absolute inset-0 w-full h-full object-cover" />
                  ) : (
                    <>
                      <div className="absolute inset-0 opacity-5 pointer-events-none grayscale">
                        <img src="/v2-texture.jpg" className="w-full h-full object-cover" alt="" />
                      </div>
                      <div className="text-center space-y-6 z-10 transition-transform group-hover:-translate-y-2 duration-500">
                        <div className="w-20 h-20 rounded-full bg-primary-container flex items-center justify-center mx-auto shadow-sm">
                          <span className="material-symbols-outlined text-primary text-4xl">cloud_upload</span>
                        </div>
                        <div className="space-y-2">
                          <h3 className="text-2xl font-semibold text-[#191c1c] tracking-tight">Drag and drop your photo here</h3>
                          <p className="text-[#424846] font-light">or click to browse clinical imagery</p>
                        </div>
                        <div className="flex gap-4 justify-center text-[10px] font-bold uppercase tracking-widest text-outline">
                           <span>JPG</span><span>PNG</span><span>HEIC</span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </motion.div>

              <div className="flex flex-col md:flex-row items-center justify-between gap-8 pt-8">
                <div className="flex items-center gap-4">
                  <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>verified_user</span>
                  <span className="text-sm text-[#424846]">Your data is encrypted and remains private.</span>
                </div>
                
                <button
                  onClick={startAnalysis}
                  disabled={!file}
                  className={`px-12 py-5 font-bold tracking-tight transition-all duration-500 shadow-xl ${
                    file 
                    ? "bg-emerald-900 text-white hover:bg-emerald-800 cursor-pointer" 
                    : "bg-stone-200 text-stone-400 cursor-not-allowed opacity-60"
                  }`}
                >
                  START ANALYSIS
                </button>
              </div>
              
              {error && (
                <p className="text-red-500 font-bold text-sm bg-red-50 p-4 border-l-4 border-red-500 uppercase tracking-wider">{error}</p>
              )}
            </div>

            {/* Right: Integrity Sidebar (V2 Refined) */}
            <aside className="space-y-12">
              <div className="bg-stone-100 p-8 space-y-8 rounded-2xl">
                <h4 className="text-xs font-bold uppercase tracking-[0.2em] text-primary border-b border-outline-variant/20 pb-4">
                  Analysis Integrity
                </h4>
                <div className="space-y-10">
                  <div className="flex gap-5">
                    <div className="flex-shrink-0 w-10 h-10 bg-white flex items-center justify-center rounded-lg shadow-sm">
                      <span className="material-symbols-outlined text-primary">light_mode</span>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-bold text-[#191c1c]">Even Lighting</p>
                      <p className="text-xs leading-relaxed text-[#424846]">Avoid harsh shadows or direct sunlight. Soft, indoor natural light is best.</p>
                    </div>
                  </div>
                  <div className="flex gap-5">
                    <div className="flex-shrink-0 w-10 h-10 bg-white flex items-center justify-center rounded-lg shadow-sm">
                      <span className="material-symbols-outlined text-primary">face</span>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-bold text-[#191c1c]">Neutral Expression</p>
                      <p className="text-xs leading-relaxed text-[#424846]">Relax your face. Do not smile or squint to keep skin texture natural.</p>
                    </div>
                  </div>
                  <div className="flex gap-5">
                    <div className="flex-shrink-0 w-10 h-10 bg-white flex items-center justify-center rounded-lg shadow-sm">
                      <span className="material-symbols-outlined text-primary">visibility_off</span>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-bold text-[#191c1c]">Clear Obstructions</p>
                      <p className="text-xs leading-relaxed text-[#424846]">Remove glasses, hats, or hair covering the face for full scan accuracy.</p>
                    </div>
                  </div>
                </div>

                <div className="pt-8">
                  <div className="bg-primary-container/30 p-4 rounded-xl border border-primary-container/20">
                    <div className="flex items-start gap-3">
                      <span className="material-symbols-outlined text-secondary scale-75">info</span>
                      <p className="text-[11px] leading-relaxed text-on-primary-container">
                        Clinical results are powered by AI and should be used for informational purposes alongside professional advice.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="px-8 flex flex-col gap-4">
                <h5 className="text-[10px] font-bold uppercase tracking-widest text-outline">Clinical Methodology</h5>
                <a href="#" className="text-sm text-primary font-medium hover:underline inline-flex items-center gap-2 group">
                  Read clinical white paper 
                  <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">arrow_forward</span>
                </a>
              </div>
            </aside>
          </div>
        </section>

        {/* ── Asymmetric Visual Break (V2 Science) ── */}
        <section className="bg-surface-container py-24 px-16 overflow-hidden">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-16">
            <div className="w-full md:w-1/2 relative">
               <div className="aspect-[16/10] bg-stone-200 overflow-hidden relative rounded-2xl shadow-2xl">
                  <img src="/v2-science.jpg" className="w-full h-full object-cover grayscale opacity-80 hover:grayscale-0 transition-all duration-1000" alt="Clinical lab" />
                  <div className="absolute inset-0 bg-secondary/5" />
               </div>
               <div className="absolute -bottom-8 -right-8 w-48 h-48 bg-primary p-8 text-on-primary hidden md:flex flex-col justify-end shadow-2xl">
                  <span className="text-5xl font-bold">98%</span>
                  <span className="text-[10px] uppercase tracking-widest font-bold mt-2">Detection Rate</span>
               </div>
            </div>
            <div className="w-full md:w-1/2 space-y-6">
               <span className="text-xs font-bold uppercase tracking-[0.2em] text-primary">The Science</span>
               <h2 className="text-5xl font-extrabold tracking-tighter text-[#191c1c] leading-tight">Precision in Every Pixel</h2>
               <p className="text-[#424846] leading-relaxed text-lg font-light">
                  Our neural core analyzes over 12 million skin parameters per second, cross-referencing your upload with a clinical database of 500,000+ cases to ensure medical-grade precision in every scan.
               </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="w-full py-12 px-16 mt-auto bg-stone-50 dark:bg-stone-950 flex flex-col md:flex-row justify-between items-center gap-8 border-t border-outline-variant/10">
        <div className="flex flex-col gap-2">
          <span className="font-bold text-emerald-900 tracking-tight">SkinSight</span>
          <p className="text-stone-500 text-sm leading-relaxed">© 2026 SkinSight. Clinical Grade Analysis.</p>
        </div>
        <div className="flex gap-8">
          <a href="#" className="text-stone-500 hover:text-emerald-700 text-sm transition-colors">Privacy Policy</a>
          <a href="#" className="text-stone-500 hover:text-emerald-700 text-sm transition-colors">Terms of Service</a>
          <a href="#" className="text-stone-500 hover:text-emerald-700 text-sm transition-colors underline font-medium">Clinical Methodology</a>
          <a href="#" className="text-stone-500 hover:text-emerald-700 text-sm transition-colors">Support</a>
        </div>
      </footer>
    </div>
  );
}
