"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import Image from "next/image";

export default function LoginPage() {
  const router = useRouter();
  const [phoneNumber, setPhoneNumber] = useState("");
  const [countryCode, setCountryCode] = useState("+91");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeInfo, setActiveInfo] = useState<string | null>(null);

  const infoContent: Record<string, any> = {
    clinical: {
      label: "Scientific Foundation",
      title: "Clinical Standards & Methodology",
      description: "Our diagnostic engine is built on a foundation of peer-reviewed clinical data and continuous validation by board-certified dermatologists.",
      pillars: [
        { label: "Accuracy", title: "Diagnostic Sensitivity", text: "SkinSight's Vision-Transformer architecture achieves a 94.2% sensitivity rate for common inflammatory conditions, providing professional-grade screenings." },
        { label: "Protocol", title: "Certified Pipeline", text: "Our analysis follows ISO 27001 data integrity standards and aligns with the highest international clinical laboratory guidelines." },
        { label: "Science", title: "Vision Analytics", text: "We utilize multi-spectral zone mapping to detect sub-surface pigmentation and vascular irregularities invisible to the naked eye." }
      ]
    },
    privacy: {
      label: "Data Security",
      title: "Biometric Privacy Sanctuary",
      description: "Your biometric and biographic data are treated with the highest level of clinical confidentiality and encrypted at the source.",
      pillars: [
        { label: "Security", title: "End-to-End Encryption", text: "All facial imagery is encrypted at the device level during capture. We never store raw image files in an unencrypted state." },
        { label: "Control", title: "Data Sovereignty", text: "You maintain 100% ownership of your profile. We never share or sell biometric markers to third-party insurance or marketing entities." },
        { label: "Compliance", title: "HIPAA Alignment", text: "Our storage architecture is built to exceed standard healthcare privacy regulations, ensuring your sanctuary remains secure." }
      ]
    },
    terms: {
      label: "User Agreement",
      title: "Clinical Service Protocol",
      description: "By using SkinSight, you acknowledge the parameters and clinical scope of our automated screening technology.",
      disclaimers: [
        { label: "Scope", title: "Medical Disclaimer", text: "SkinSight is a screening tool, not a diagnostic medical device. It should used to inform, not replace, clinical judgment." },
        { label: "Eligibility", title: "Usage Requirements", text: "Service is restricted to individuals aged 18 and over. Use of the platform implies consent to our automated data processing protocol." },
        { label: "Reliability", title: "Technology Parameters", text: "While high-precision, AI screenings are subject to lighting and image quality variables. Final assessments should be made by a physician." }
      ]
    },
    contact: {
      label: "Support Hub",
      title: "Direct Professional Connection",
      description: "Our specialized support team and data privacy officers are available for professional inquiries and technical assistance.",
      contactGrid: true
    }
  };

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phoneNumber.length === 10) {
      setLoading(true);
      setError("");
      try {
        const response = await fetch("http://localhost:8000/api/auth/send-otp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ phone: phoneNumber }),
        });

        const data = await response.json();

        if (response.ok) {
          const prevPhone = localStorage.getItem("userPhone");
          if (prevPhone && prevPhone !== phoneNumber) {
            localStorage.removeItem("userDetails");
            localStorage.removeItem("userConcerns");
            localStorage.removeItem("skinSightAnalysis");
          }
          localStorage.setItem("userPhone", phoneNumber);
          router.push("/otp");
        } else {
          setError(data.detail || "Failed to send OTP. Please try again.");
        }
      } catch (err) {
        setError("Network error. Is the backend server running?");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="login-page">
      {/* ── Top Nav Bar (Glass) ── */}
      <nav className="login-nav">
        <div className="login-nav-inner">
          <Link href="/" className="login-logo">SkinSight</Link>
          <div className="login-nav-links">
            {/* Links removed for focused clinical access */}
          </div>
          <div className="login-nav-icons">
            {/* Global navigation icons removed for clinical privacy */}
          </div>
        </div>
      </nav>

      {/* ── Main Content: Split Layout ── */}
      <main className="login-main">
        {/* Left Side: Editorial Image */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="login-hero-section"
        >
          <div className="login-hero-image-wrapper">
            <Image
              src="/hero-serum.jpg"
              alt="Macro clinical texture of organic face serum"
              fill
              className="login-hero-image"
              priority
            />
            {/* Editorial Overlay */}
            <div className="login-hero-overlay">
              <h2 className="login-hero-title" style={{ color: 'black', mixBlendMode: 'normal' }}>
                Science-backed radiance.
              </h2>
              <p className="login-hero-subtitle" style={{ color: 'black' }}>
                Welcome to the next generation of clinical dermatology, where precision meets personalized care.
              </p>
            </div>
          </div>
          {/* Gradient bleed to right side */}
          <div className="login-hero-gradient-bleed" />
        </motion.div>

        {/* Right Side: Login Form */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.15, ease: "easeOut" }}
          className="login-form-section"
        >
          <div className="login-form-container">
            {/* Branding Context */}
            <div className="login-form-header">
              <span className="login-form-label">Clinical Access</span>
              <h1 className="login-form-title">Welcome Back</h1>
              <p className="login-form-desc">Enter your credentials to access your skin profile.</p>
            </div>

            {/* Form */}
            <form className="login-form" onSubmit={handleSendOTP}>
              {/* Phone Input */}
              <div className="login-field">
                <label className="login-field-label">Phone Number</label>
                <div className="login-phone-row">
                  <div className="login-country-select-wrapper">
                    <select
                      className="login-country-select"
                      value={countryCode}
                      onChange={(e) => setCountryCode(e.target.value)}
                    >
                      <option value="+91">+91</option>
                      <option value="+1">+1</option>
                      <option value="+44">+44</option>
                      <option value="+61">+61</option>
                    </select>
                    <svg className="login-select-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </div>
                  <input
                    type="tel"
                    maxLength={10}
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ""))}
                    placeholder="000 000 0000"
                    className="login-phone-input"
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="login-error"
                >
                  {error}
                </motion.div>
              )}

              {/* CTA Actions */}
              <div className="login-cta-group">
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  type="submit"
                  disabled={phoneNumber.length !== 10 || loading}
                  className={`login-proceed-btn ${phoneNumber.length !== 10 || loading ? "login-proceed-btn--disabled" : ""}`}
                >
                  {loading ? "Sending..." : "Proceed"}
                </motion.button>

              </div>
            </form>
          </div>
        </motion.div>
      </main>

      <AnimatePresence>
        {activeInfo && infoContent[activeInfo] && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="modal-overlay"
            onClick={() => setActiveInfo(null)}
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              className="modal-container"
              onClick={(e) => e.stopPropagation()}
            >
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
                <p className="section-description" style={{ fontSize: '1.1rem', marginBottom: '3rem' }}>
                  {infoContent[activeInfo].description}
                </p>

                {infoContent[activeInfo].pillars && (
                  <div className="content-grid">
                    {infoContent[activeInfo].pillars.map((pillar: any, idx: number) => (
                      <div key={idx} className="clinical-pillar">
                        <span className="pill-label">{pillar.label}</span>
                        <h3 className="detail-title" style={{ marginBottom: '0.5rem' }}>{pillar.title}</h3>
                        <p className="detail-text">{pillar.text}</p>
                      </div>
                    ))}
                  </div>
                )}

                {infoContent[activeInfo].contactGrid && (
                  <div className="contact-info-grid" style={{ marginTop: '0' }}>
                    <div className="contact-item">
                      <div className="contact-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></div>
                      <h3 className="detail-title">Clinical Support</h3>
                      <p className="detail-text">+1 (650) 555-0142<br/>Mon-Fri, 9am - 6pm PST</p>
                    </div>
                    <div className="contact-item">
                      <div className="contact-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
                      <h3 className="detail-title">Email Correspondence</h3>
                      <p className="detail-text">clinical@skinsight-ai.com<br/>24/7 Priority Response</p>
                    </div>
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
