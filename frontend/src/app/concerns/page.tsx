"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";

const CONCERNS = [
  { 
    id: "acne", 
    label: "INFLAMMATORY",
    title: "Acne / Pimples", 
    description: "Comedonal, blackheads or pus-filled pimples targeting sebum regulation.",
    image: "/acne-intake.png"
  },
  { 
    id: "dark_spots", 
    label: "PIGMENTARY",
    title: "Dark Spots / Marks", 
    description: "Flat spots and melanin buildup due to UV exposure or post-breakout marks.",
    image: "/spots-intake.png"
  },
  { 
    id: "acne_scars", 
    label: "STRUCTURAL",
    title: "Acne Scars", 
    description: "Pits or texture irregularities remaining after severe or prolonged inflammation.",
    image: "/scars-intake.png"
  },
  { 
    id: "pigmentation", 
    label: "TONE CALIBRATION",
    title: "Pigmentation", 
    description: "Irregular dark patches and uneven melanin distribution across the skin surface.",
    image: "/pigment-intake.png"
  },
  { 
    id: "dull_skin", 
    label: "RADIANCE INDEX",
    title: "Dull Skin", 
    description: "Skin that lacks lustre, appearing flat or grey due to poor light refraction.",
    image: "/dull-intake.png"
  },
  { 
    id: "dark_circles", 
    label: "ORBITAL INTEGRITY",
    title: "Dark Circles", 
    description: "Darkened area below the eyes, often linked to vascularity or skin thinning.",
    image: "/circles-intake.png"
  }
];

export default function PrimaryConcernPage() {
  const router = useRouter();
  const [selected, setSelected] = useState("");
  const [activeInfo, setActiveInfo] = useState<string | null>(null);

  useEffect(() => {
    const isVerified = localStorage.getItem("isVerified");
    if (!isVerified) router.push("/login");
  }, [router]);

  const handleContinue = () => {
    if (selected) {
      localStorage.setItem("primaryConcern", selected);
      router.push("/concerns/secondary");
    }
  };

  const infoContent: Record<string, any> = {
    clinical: {
      label: "Scientific Foundation",
      title: "Clinical Standards & Methodology",
      description: "Our diagnostic engine is built on a foundation of peer-reviewed clinical data and continuous validation by board-certified dermatologists.",
      pillars: [
        { label: "Accuracy", title: "Diagnostic Sensitivity", text: "SkinSight's Vision-Transformer architecture achieves a 94.2% sensitivity rate for common inflammatory conditions." },
        { label: "Protocol", title: "Certified Pipeline", text: "Our analysis follows ISO 27001 data integrity standards and aligns with the highest international clinical laboratory guidelines." }
      ]
    },
    privacy: {
      label: "Data Security",
      title: "Biometric Privacy Sanctuary",
      description: "Your biometric and biographic data are treated with the highest level of clinical confidentiality and encrypted at the source.",
      pillars: [
        { label: "Security", title: "End-to-End Encryption", text: "All facial imagery is encrypted at the device level during capture. We never store raw image files in an unencrypted state." }
      ]
    },
    terms: {
      label: "User Agreement",
      title: "Clinical Service Protocol",
      description: "By using SkinSight, you acknowledge the parameters and clinical scope of our automated screening technology.",
      pillars: [
        { label: "Scope", title: "Medical Disclaimer", text: "SkinSight is a screening tool, not a diagnostic medical device. It should used to inform, not replace, clinical judgment." }
      ]
    },
    contact: {
      label: "Support Hub",
      title: "Direct Professional Connection",
      description: "Our specialized support team and data privacy officers are available for professional inquiries and technical assistance.",
      contactGrid: true
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
          <span className="diagnostic-header-label">PERSONALIZED DIAGNOSIS</span>
          <h1 className="diagnostic-main-title">Choose your most important concern</h1>
        </div>

        {/* Diagnostic Card Grid */}
        <div className="diagnostic-grid">
          {CONCERNS.map((concern, idx) => (
            <motion.div
              key={concern.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.6, ease: "easeOut" }}
              onClick={() => setSelected(concern.id)}
              className={`concern-card ${selected === concern.id ? "concern-card--selected" : ""}`}
            >
              <div className="concern-image-wrapper">
                <Image
                  src={concern.image}
                  alt={concern.title}
                  fill
                  className="concern-image"
                />
              </div>
              <div className="concern-content">
                <span className="concern-label">{concern.label}</span>
                <h3 className="concern-title">{concern.title}</h3>
                <p className="concern-description">{concern.description}</p>
                
                <div className="concern-select-link">
                  {selected === concern.id ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#191c1c' }}>
                       <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                       SELECTED
                    </span>
                  ) : (
                    "SELECT CONCERN →"
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <button
            onClick={handleContinue}
            disabled={!selected}
            className={`login-proceed-btn ${!selected ? "login-proceed-btn--disabled" : ""}`}
            style={{ width: 'auto', padding: '1.4rem 5rem', borderRadius: '0.5rem' }}
          >
            CONTINUE TO ANALYSIS ⏏
          </button>
          <div className="login-form-desc" style={{ marginTop: '1.5rem', color: '#a8a29e' }}>
            Biometric diagnostic data is transmitted via end-to-end encrypted protocols.
          </div>
        </div>
      </main>

      <AnimatePresence>
        {activeInfo && infoContent[activeInfo] && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="modal-overlay" onClick={() => setActiveInfo(null)}>
            <motion.div initial={{ scale: 0.95, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.95, opacity: 0, y: 20 }} className="modal-container" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <div>
                  <span className="section-label" style={{ marginBottom: '0.5rem' }}>{infoContent[activeInfo].label}</span>
                  <h2 className="login-form-title" style={{ fontSize: '2.25rem' }}>{infoContent[activeInfo].title}</h2>
                </div>
                <button className="modal-close-btn" onClick={() => setActiveInfo(null)}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
              </div>
              <div className="modal-body">
                <p className="section-description" style={{ fontSize: '1.1rem', marginBottom: '3rem' }}>{infoContent[activeInfo].description}</p>
                {infoContent[activeInfo].pillars && (
                  <div className="content-grid">
                    {infoContent[activeInfo].pillars.map((pillar: any, idx: number) => (
                      <div key={idx} className="clinical-pillar">
                        <span className="pill-label">{pillar.label}</span>
                        <h3 className="detail-title">{pillar.title}</h3>
                        <p className="detail-text">{pillar.text}</p>
                      </div>
                    ))}
                  </div>
                )}
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
            <a href="#" onClick={(e) => { e.preventDefault(); setActiveInfo('clinical'); }}>Clinical Standards</a>
            <a href="#" onClick={(e) => { e.preventDefault(); setActiveInfo('privacy'); }}>Privacy Policy</a>
            <a href="#" onClick={(e) => { e.preventDefault(); setActiveInfo('terms'); }}>Terms of Service</a>
            <a href="#" onClick={(e) => { e.preventDefault(); setActiveInfo('contact'); }}>Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
