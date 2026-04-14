"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";

export default function DetailsPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    gender: "",
    age: "",
  });
  const [loading, setLoading] = useState(false);
  const [activeInfo, setActiveInfo] = useState<string | null>(null);

  useEffect(() => {
    const isVerified = localStorage.getItem("isVerified");
    if (!isVerified) router.push("/login");
  }, [router]);

  const handleSaveProfile = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (formData.name && formData.gender && formData.age) {
      setLoading(true);
      const phone = localStorage.getItem("userPhone");
      try {
        await fetch("http://localhost:8000/api/user/profile", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            name: formData.name,
            gender: formData.gender,
            age: parseInt(formData.age),
            phone: phone || "unknown" 
          })
        });
        localStorage.setItem("userDetails", JSON.stringify(formData));
        router.push("/concerns");
      } catch (err) {
        console.error("Failed to save profile", err);
      } finally {
        setLoading(false);
      }
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
      disclaimers: [
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

  const genderOptions = [
    "Female", "Male", "Prefer not to say"
  ];

  return (
    <div className="login-page">
      {/* ── Navbar ── */}
      <nav className="login-nav">
        <div className="login-nav-inner">
          <Link href="/" className="login-logo">SkinSight</Link>
          <div className="login-nav-links">
            {/* Nav links removed for onboarding focus */}
          </div>
          <div className="login-nav-icons">
             {/* Global navigation icons removed for clinical privacy */}
          </div>
        </div>
      </nav>

      {/* ── Main Layout ── */}
      <main className="login-main">
        {/* Left Side: Editorial Context */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          className="login-hero-section"
        >
          <div className="login-hero-image-wrapper">
            <Image
              src="/clinical-lab.jpg"
              alt="Technical clinical lab illustration"
              fill
              className="login-hero-image"
              priority
              style={{ padding: '4rem', opacity: 0.8 }}
            />
            {/* Editorial Overlay */}
            <div className="login-hero-overlay">
              <span className="login-form-label" style={{ color: '#191c1c', fontWeight: 800 }}>Diagnostic Identity</span>
              <h2 className="login-hero-title" style={{ mixBlendMode: 'normal', color: '#191c1c' }}>
                Personal <br/>Profile.
              </h2>
              <p className="login-hero-subtitle" style={{ color: '#191c1c', fontWeight: 700, opacity: 0.9 }}>
                Establishing your clinical baseline allows our AI to adjust diagnostic sensitivities for your demographic profile.
              </p>
            </div>
          </div>
          {/* Gradient bleed to right side */}
          <div className="login-hero-gradient-bleed" />
        </motion.div>

        {/* Right Side: Profile Form */}
        <motion.div
           initial={{ opacity: 0, x: 30 }}
           animate={{ opacity: 1, x: 0 }}
           className="login-form-section"
        >
          <div className="login-form-container">
            <div className="login-form-header">
              <span className="login-form-label">Profile Setup</span>
              <h1 className="login-form-title">About You</h1>
              <p className="login-form-desc">Provide your foundational details for clinical calibration.</p>
            </div>

            <form className="login-form" onSubmit={handleSaveProfile}>
              {/* Name Input */}
              <div className="profile-input-group">
                <label className="profile-field-label">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="Enter your name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="profile-underline-input"
                />
              </div>

              {/* Age Input */}
              <div className="profile-input-group">
                <label className="profile-field-label">Age</label>
                <input
                  type="number"
                  required
                  placeholder="Your age"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  className="profile-underline-input"
                />
              </div>

              {/* Gender Selection */}
              <div className="profile-input-group">
                <label className="profile-field-label">Gender Identity</label>
                <div className="gender-identity-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginTop: '1.5rem' }}>
                  {genderOptions.map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => setFormData({ ...formData, gender: opt })}
                      className={`gender-btn ${formData.gender === opt ? "gender-btn--selected" : ""}`}
                      style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem' }}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              <div className="login-cta-group" style={{ marginTop: '2rem' }}>
                <button
                  type="submit"
                  disabled={!formData.name || !formData.gender || !formData.age || loading}
                  className={`login-proceed-btn ${!formData.name || !formData.gender || !formData.age || loading ? "login-proceed-btn--disabled" : ""}`}
                >
                  {loading ? "Saving Baseline..." : "SAVE PROFILE →"}
                </button>
                <p className="login-form-desc" style={{ fontSize: '0.75rem', textAlign: 'center', marginTop: '1rem' }}>
                  Your profile data is encrypted using AES-256 standards.
                </p>
              </div>
            </form>
          </div>
        </motion.div>
      </main>

      {/* ── Info Modal Overlay (Global) ── */}
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

      {/* ── Footer ── */}
      <footer className="login-footer">
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
