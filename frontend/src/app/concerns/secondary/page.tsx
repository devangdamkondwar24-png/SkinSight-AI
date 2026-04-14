"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";

const SECONDARY_CONCERNS = [
  "Open Pores",
  "Blackheads / Whiteheads",
  "Fine lines / Wrinkles",
  "Bumpy texture",
  "Skin redness",
  "Uneven Skin Tone",
  "Dry / Flaky Skin",
  "Skin Sensitivity",
  "Oiliness / Shine"
];

export default function SecondaryConcernsPage() {
  const router = useRouter();
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeInfo, setActiveInfo] = useState<string | null>(null);

  useEffect(() => {
    const isVerified = localStorage.getItem("isVerified");
    if (!isVerified) router.push("/login");
  }, [router]);

  const toggleConcern = (concern: string) => {
    if (selected.includes(concern)) {
      setSelected(selected.filter((c) => c !== concern));
    } else if (selected.length < 3) {
      setSelected([...selected, concern]);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    const phone = localStorage.getItem("userPhone");
    const primary = localStorage.getItem("primaryConcern") || "unknown";
    
    try {
      await fetch("http://localhost:8000/api/user/concerns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          phone: phone || "unknown",
          primary_concern: primary,
          secondary_concerns: selected
        })
      });
      localStorage.setItem("userConcerns", JSON.stringify(selected));
      router.push("/analysis"); 
    } catch (err) {
      console.error("Failed to save concerns", err);
    } finally {
      setLoading(false);
    }
  };

  const infoContent: Record<string, any> = {
    clinical: {
      label: "Scientific Foundation",
      title: "Clinical Standards & Methodology",
      description: "Our diagnostic engine is built on a foundation of peer-reviewed clinical data and continuous validation by board-certified dermatologists.",
      pillars: [
        { label: "Accuracy", title: "Diagnostic Sensitivity", text: "SkinSight's Vision-Transformer architecture achieves a 94.2% sensitivity rate for common inflammatory conditions." }
      ]
    },
    privacy: {
      label: "Data Security",
      title: "Biometric Privacy Sanctuary",
      description: "Your biometric and biographic data are treated with the highest level of clinical confidentiality and encrypted at the source.",
      pillars: [
        { label: "Security", title: "End-to-End Encryption", text: "All facial imagery is encrypted at the device level during capture." }
      ]
    }
  };

  return (
    <div className="login-page">
      {/* ── Precision Navbar ── */}
      <nav className="login-nav">
        <div className="login-nav-inner" style={{ justifyContent: 'center' }}>
          <div style={{ position: 'absolute', left: '2rem' }}>
            <Link href="/" className="login-logo">SkinSight</Link>
          </div>
          <div className="login-nav-links" />
        </div>
      </nav>

      {/* ── Main Diagnostic Dashboard ── */}
      <main className="diagnostic-dashboard">
        {/* Header Section */}
        <div className="login-form-header" style={{ alignItems: 'center', marginBottom: '5rem' }}>
          <span className="diagnostic-header-label">COMPLEMENTARY IDENTIFIERS</span>
          <h1 className="diagnostic-main-title">Secondary Characteristics</h1>
          <p className="section-description" style={{ textAlign: 'center', marginTop: '1rem' }}>
            Please select up to 3 additional traits you would like our AI to monitor during analysis.
          </p>
        </div>

        {/* Clinical Chip Grid */}
        <div className="identifier-grid">
          {SECONDARY_CONCERNS.map((concern, idx) => (
            <motion.button
              key={concern}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05, duration: 0.4 }}
              onClick={() => toggleConcern(concern)}
              className={`identifier-chip ${selected.includes(concern) ? "identifier-chip--selected" : ""}`}
            >
              <span className="chip-text">{concern}</span>
              <div className="chip-status">
                {selected.includes(concern) && (
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                )}
              </div>
            </motion.button>
          ))}
        </div>

        {/* Bottom CTA */}
        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <button
            onClick={handleComplete}
            disabled={loading}
            className={`login-proceed-btn ${loading ? "login-proceed-btn--disabled" : ""}`}
            style={{ width: 'auto', padding: '1.4rem 5rem', borderRadius: '0.5rem' }}
          >
            {loading ? "SAVING CLINICAL DATA..." : "FINISH CLINICAL SETUP ⏏"}
          </button>
          <div className="login-form-desc" style={{ marginTop: '1.5rem', color: '#a8a29e' }}>
            Selected traits: {selected.length} / 3
          </div>
        </div>
      </main>

      <AnimatePresence>
        {activeInfo && infoContent[activeInfo] && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="modal-overlay" onClick={() => setActiveInfo(null)}>
            <motion.div initial={{ scale: 0.95, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.95, opacity: 0, y: 20 }} className="modal-container" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2 className="login-form-title" style={{ fontSize: '2rem' }}>{infoContent[activeInfo].title}</h2>
                <button className="modal-close-btn" onClick={() => setActiveInfo(null)}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
              </div>
              <div className="modal-body">
                <p className="section-description">{infoContent[activeInfo].description}</p>
              </div>
              <div className="modal-footer">
                <button className="modal-footer-btn" onClick={() => setActiveInfo(null)}>Dismiss</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="login-footer" style={{ borderTop: '1px solid rgba(194, 200, 197, 0.4)', marginTop: '6rem' }}>
        <div className="login-footer-inner">
          <div className="login-footer-brand">
            <div className="login-footer-brand-name">SkinSight Clinical Labs</div>
            <div className="login-footer-copyright">© 2026 SkinSight Clinical Labs</div>
          </div>
          <div className="login-footer-links">
            <a href="#" onClick={(e) => { e.preventDefault(); setActiveInfo('privacy'); }}>Privacy Policy</a>
            <a href="#" onClick={(e) => { e.preventDefault(); }}>Terms of Service</a>
            <a href="#" onClick={(e) => { e.preventDefault(); }}>Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
