"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import { CheckCircle, Sparkles, AlertCircle, Beaker, Droplets, ShieldCheck, ArrowRight, Activity, Zap, X, ShoppingBag, Info } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

function ProductModal({ isOpen, onClose, step }: { isOpen: boolean, onClose: () => void, step: any }) {
  if (!isOpen || !step) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
        />
        <motion.div 
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          className="relative bg-white rounded-[40px] w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col"
        >
          {/* Header */}
          <div className="p-10 border-b border-stone-100 flex justify-between items-center bg-stone-50/50">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-[#004d40] mb-2">Clinical Recommendations</p>
              <h3 className="text-3xl font-bold tracking-tighter italic">Recommended for {step.title || step.action}</h3>
            </div>
            <button onClick={onClose} className="p-3 bg-white rounded-full shadow-sm hover:bg-stone-100 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-10 no-scrollbar">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {step.recommended_products?.map((product: any, i: number) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="group bg-[#f8faf9] rounded-3xl p-8 hover:bg-[#eceeed] transition-all duration-500 border border-stone-100"
                >
                  <div className="flex flex-col justify-between h-full">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-widest text-[#004d40] mb-2">{product.brand}</p>
                      <h4 className="text-xl font-bold leading-tight mb-3">{product.name}</h4>
                      <p className="text-sm text-[#424846] font-light leading-relaxed">
                        <span className="font-bold">Clinical Benefit:</span> {product.benefit}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-12 bg-[#d1e8e2]/30 rounded-3xl p-8 border border-white">
              <div className="flex items-center gap-4 mb-4">
                <Info className="w-5 h-5 text-[#004d40]" />
                <h5 className="font-bold">Dermatologist's Note</h5>
              </div>
              <p className="text-sm text-[#424846] leading-relaxed font-light">
                {step.detail} These products have been selected because they contain the target concentration of 
                <span className="font-bold"> {step.ingredients?.join(", ")}</span> as synthesized in your analysis.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

export default function TreatmentsPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [predictions, setPredictions] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedStep, setSelectedStep] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const phone = localStorage.getItem("userPhone");
    if (!phone) {
      router.push("/analysis");
      return;
    }

    const fetchAnalysis = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/user/analysis/${phone}/latest`);
        if (!response.ok) throw new Error("No recent analysis found");
        
        const result = await response.json();
        setData(result);
        
        // Fetch ML Predictions
        try {
          const mlResponse = await fetch(`http://localhost:8000/api/predict-progression`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              lesion_count: result.analysis?.lesion_count || 15,
              severity: result.analysis?.acne_severity?.grade || 'Moderate',
              pigmentation: result.analysis?.hyperpigmentation?.coverage_pct || 10.0,
              age: 25, // Fallback profile standard
              skin_type: 'Combination'
            })
          });
          if (mlResponse.ok) {
            const mlResult = await mlResponse.json();
            setPredictions(mlResult);
          }
        } catch (mlError) {
          console.warn("ML Model fetching failed: ", mlError);
        }
        
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysis();
  }, [router]);

  const openProductModal = (step: any, time: string) => {
    setSelectedStep({
      ...step,
      timeLabel: time,
      title: step.action
    });
    setIsModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#f8faf9] flex items-center justify-center">
        <Activity className="animate-spin text-[#004d40] w-12 h-12" />
      </div>
    );
  }

  const userImage = data?.image?.base64 
    ? `data:image/jpeg;base64,${data.image.base64}` 
    : "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&q=80&w=1280";

  const imageShortTerm = data?.image?.short_term_base64
    ? `data:image/jpeg;base64,${data.image.short_term_base64}`
    : userImage;

  const imageLongTerm = data?.image?.long_term_base64
    ? `data:image/jpeg;base64,${data.image.long_term_base64}`
    : userImage;

  const amRoutine = data?.recommendations?.am_routine || [];
  const pmRoutine = data?.recommendations?.pm_routine || [];

  return (
    <main className="min-h-screen bg-[#f8faf9] text-[#191c1c] pb-40 overflow-x-hidden">
      <Navbar />
      <ProductModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} step={selectedStep} />

      {/* ── Hero Section ── */}
      <section className="pt-48 pb-24 px-16 max-w-[1440px] mx-auto flex flex-col md:flex-row items-end gap-16">
        <div className="md:w-2/3">
          <motion.h4 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-[10px] font-black uppercase tracking-[0.3em] text-[#004d40] mb-6 flex items-center gap-2"
          >
            <Zap className="w-3 h-3" /> Synthesis Analysis
          </motion.h4>
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-7xl md:text-[9rem] font-bold tracking-tighter leading-[0.85] text-[#191c1c] mb-10"
          >
            Treatment<br/>& Progress.
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-[#424846] max-w-xl leading-relaxed font-light"
          >
            A longitudinal view of your dermal evolution. Leveraging high-resolution scan synthesis to predict and track your cellular journey.
          </motion.p>
        </div>
      </section>

      {/* ── Progress Tracking ── */}
      <section className="px-16 max-w-[1440px] mx-auto mb-60 space-y-32">
        {/* Stage 1: Now */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-24 items-center"
        >
          <div className="relative group">
            <div className="aspect-[4/5] bg-stone-100 rounded-[50px] overflow-hidden relative shadow-2xl border border-white/20">
              <img src={userImage} className="w-full h-full object-cover" alt="Baseline" />
            </div>
            <div className="absolute top-10 left-10 bg-[#004d40] text-white px-6 py-2 text-[10px] tracking-[0.2em] font-black uppercase rounded-full z-20">Now</div>
          </div>
          <div className="space-y-10">
            <h2 className="text-5xl font-bold tracking-tighter">Initial Scan Analysis</h2>
            <ul className="space-y-6">
              {[
                { label: "Acne Severity", text: data?.analysis?.acne_severity?.grade || "Moderate", icon: AlertCircle, color: "text-red-500" },
                { label: "Lesion Density", text: `${data?.analysis?.lesion_count || 0} Identified markers`, icon: Activity, color: "text-[#004d40]" },
                { label: "Barrier Status", text: "Compromised epidermal integrity detected.", icon: ShieldCheck, color: "text-stone-400" }
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-6 border-l-2 border-stone-200 pl-8 py-2">
                  <item.icon className={`w-6 h-6 ${item.color} mt-1`} />
                  <div>
                    <p className="text-xs font-black uppercase tracking-widest text-stone-300 mb-1">{item.label}</p>
                    <p className="text-lg text-[#191c1c] italic">{item.text}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </motion.div>

        {/* Stage 2: 2-4 Weeks */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-24 items-center"
        >
          <div className="space-y-10 order-2 md:order-1">
            <div className="text-right">
              <h2 className="text-5xl font-bold tracking-tighter mb-4">Stabilization Phase</h2>
              <p className="text-black font-bold uppercase tracking-widest text-xs">2-4 Week Prediction</p>
            </div>
            <ul className="space-y-6">
              {[
                { label: "Target Lesion Count", text: `Predicted reduction to ${predictions?.short_term?.lesion_count_prediction ?? "~"} markers.`, icon: Activity, color: "text-[#004d40]" },
                { label: "Predicted Severity", text: `Clinical grade expected to reach ${predictions?.short_term?.severity_prediction ?? "Mild"}.`, icon: CheckCircle, color: "text-[#004d40]" },
                { label: "Texture & Hydration", text: "Visible refinement and restored water balance.", icon: CheckCircle, color: "text-[#004d40]" }
              ].map((item, i) => (
                <li key={i} className="flex items-start justify-end gap-6 border-r-2 border-[#d1e8e2] pr-8 py-2 text-right">
                  <div>
                    <p className="text-xs font-black uppercase tracking-widest text-stone-300 mb-1">{item.label}</p>
                    <p className="text-lg text-[#191c1c] leading-relaxed italic">{item.text}</p>
                  </div>
                  <item.icon className={`w-6 h-6 ${item.color} mt-1 shrink-0`} />
                </li>
              ))}
            </ul>
          </div>
          <div className="relative group order-1 md:order-2">
            <div className="aspect-[4/5] bg-[#d1e8e2] rounded-[50px] overflow-hidden relative shadow-2xl border border-white/20">
              <img 
                alt="Stabilization Scan" 
                className="w-full h-full object-cover transition-all duration-1000" 
                style={{ filter: "saturate(0.8) brightness(1.05) contrast(0.98)" }}
                src={imageShortTerm} 
              />
              <div className="absolute inset-0 bg-emerald-900/5 mix-blend-overlay pointer-events-none" />
            </div>
            <div className="absolute top-10 right-10 bg-[#004d40] text-white px-6 py-2 text-[10px] tracking-[0.2em] font-black uppercase rounded-full shadow-lg z-20">
              Short Term: Stabilization
            </div>
          </div>
        </motion.div>

        {/* Stage 3: 8-12 Weeks */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 gap-24 items-center"
        >
          <div className="relative group">
            <div className="aspect-[4/5] bg-emerald-50 rounded-[50px] overflow-hidden relative shadow-2xl border border-white/20">
              <img 
                alt="Equilibrium Scan" 
                className="w-full h-full object-cover transition-all duration-1000" 
                style={{ filter: "saturate(1.0) brightness(1.1) contrast(1.05)" }}
                src={imageLongTerm} 
              />
              <div className="absolute inset-0 bg-white/20 mix-blend-soft-light pointer-events-none" />
            </div>
            <div className="absolute top-10 left-10 bg-[#004d40] text-white px-6 py-2 text-[10px] tracking-[0.2em] font-black uppercase rounded-full shadow-lg z-20">
              Long Term: Equilibrium
            </div>
          </div>
          <div className="space-y-10">
            <div>
              <h2 className="text-5xl font-bold tracking-tighter mb-4 text-[#004d40]">Dermal Equilibrium</h2>
              <p className="text-black font-bold uppercase tracking-widest text-xs">8-12 Week Target</p>
            </div>
            <ul className="space-y-6">
              {[
                { label: "Target Lesion Count", text: `Predicted reduction to ${predictions?.long_term?.lesion_count_prediction ?? "~"} markers.`, icon: Sparkles, color: "text-[#004d40]" },
                { label: "Predicted Severity", text: `Clinical grade expected to achieve ${predictions?.long_term?.severity_prediction ?? "Clear"} status.`, icon: Sparkles, color: "text-[#004d40]" },
                { label: "Equilibrium", text: "Balanced dermal-epidermal junction and maximized radiance.", icon: Sparkles, color: "text-[#004d40]" }
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-6 border-l-2 border-[#004d40]/20 pl-8 py-2">
                  <item.icon className={`w-6 h-6 ${item.color} mt-1 shrink-0`} />
                  <div>
                    <p className="text-xs font-black uppercase tracking-widest text-stone-300 mb-1">{item.label}</p>
                    <p className="text-lg text-[#191c1c] leading-relaxed italic font-bold">{item.text}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </motion.div>
      </section>

      {/* ── Personalized Protocol ── */}
      <section className="px-16 max-w-[1440px] mx-auto">
        <div className="bg-[#eceeed] rounded-[80px] p-24 relative overflow-hidden">
          <div className="relative z-10">
            <div className="flex items-center gap-6 mb-12">
              <div className="w-12 h-[2px] bg-[#004d40]"></div>
              <span className="text-[10px] font-black uppercase tracking-[0.3em] text-[#004d40]">Personalized Protocol</span>
            </div>
            <h2 className="text-5xl font-bold tracking-tighter text-[#191c1c] mb-20 max-w-2xl leading-tight">
              Calibrated high-potency regimen.
            </h2>

            {/* AM Routine */}
            <div className="mb-20">
              <div className="flex items-center gap-4 mb-10">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <h3 className="text-2xl font-bold italic tracking-tight">Morning Protocol (AM)</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                {amRoutine.map((item: any, idx: number) => (
                  <div key={idx} className="group">
                    <div className="bg-white p-10 rounded-[40px] h-full transition-all duration-700 group-hover:-translate-y-4 shadow-sm hover:shadow-xl border border-white">
                      <div className="flex justify-between items-start mb-16">
                        <span className="text-[9px] font-black uppercase tracking-[0.3em] text-stone-300">STEP 0{item.step}</span>
                        <Beaker className="w-6 h-6 text-[#004d40] opacity-40 group-hover:opacity-100 transition-opacity" />
                      </div>
                      <h4 className="text-2xl font-bold mb-3 tracking-tight">{item.action}</h4>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-[#004d40] mb-8">{item.ingredients?.join(" + ")}</p>
                      <button 
                        onClick={() => openProductModal(item, "AM")}
                        className="text-[10px] font-black uppercase tracking-widest border-b-2 border-transparent hover:border-[#004d40] transition-all pb-1 flex items-center gap-2"
                      >
                        View Recommended Product <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* PM Routine */}
            <div>
              <div className="flex items-center gap-4 mb-10">
                <Droplets className="w-5 h-5 text-[#004d40]" />
                <h3 className="text-2xl font-bold italic tracking-tight">Evening Protocol (PM)</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                {pmRoutine.map((item: any, idx: number) => (
                  <div key={idx} className="group">
                    <div className="bg-white p-10 rounded-[40px] h-full transition-all duration-700 group-hover:-translate-y-4 shadow-sm hover:shadow-xl border border-white">
                      <div className="flex justify-between items-start mb-16">
                        <span className="text-[9px] font-black uppercase tracking-[0.3em] text-stone-300">STEP 0{item.step}</span>
                        <ShieldCheck className="w-6 h-6 text-[#004d40] opacity-40 group-hover:opacity-100 transition-opacity" />
                      </div>
                      <h4 className="text-2xl font-bold mb-3 tracking-tight">{item.action}</h4>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-[#004d40] mb-8">{item.ingredients?.join(" + ")}</p>
                      <button 
                         onClick={() => openProductModal(item, "PM")}
                        className="text-[10px] font-black uppercase tracking-widest border-b-2 border-transparent hover:border-[#004d40] transition-all pb-1 flex items-center gap-2"
                      >
                        View Recommended Product <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
