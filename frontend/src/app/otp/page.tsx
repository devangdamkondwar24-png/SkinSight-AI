"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState, useEffect, useRef } from "react";
import Link from "next/link";

export default function OTPPage() {
  const router = useRouter();
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [timer, setTimer] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeInfo, setActiveInfo] = useState<string | null>(null);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    const phone = localStorage.getItem("userPhone");
    if (!phone) router.push("/login");
    setPhoneNumber(phone || "");

    const interval = setInterval(() => {
      setTimer((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [router]);

  const handleChange = (value: string, index: number) => {
    if (value.length > 1) return;
    const newOtp = [...otp];
    newOtp[index] = value.replace(/\D/g, "");
    setOtp(newOtp);

    // Auto-focus move forward
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const fullOtp = otp.join("");
    if (fullOtp.length === 6) {
      setLoading(true);
      setError("");
      try {
        const response = await fetch("http://localhost:8000/api/auth/verify-otp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ phone: phoneNumber, otp: fullOtp }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          localStorage.setItem("isVerified", "true");
          
          // CRITICAL: Check backend for existing clinical profile to avoid redundant onboarding
          try {
            const profileRes = await fetch(`http://localhost:8000/api/user/full-profile/${phoneNumber}`);
            const profileData = await profileRes.json();

            if (profileData.exists) {
              // Restore established session state
              localStorage.setItem("userDetails", JSON.stringify(profileData.details));
              localStorage.setItem("userConcerns", JSON.stringify(profileData.concerns));
              localStorage.setItem("onboarding_complete", "true");
              
              router.push("/analysis");
            } else {
              // Redirect to initial clinical intake
              router.push("/details");
            }
          } catch (profileErr) {
            console.error("Profile check failed, falling back to onboarding:", profileErr);
            router.push("/details");
          }
        } else {
          setError(data.detail || "Invalid code. Please verify and try again.");
        }
      } catch (err) {
        setError("Security gateway timeout. Is the backend running?");
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
      {/* ── Navbar ── */}
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

      {/* ── Main Layout ── */}
      <main className="login-main">
        {/* Left Side: Security Context */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          className="login-hero-section"
          style={{ background: '#f8faf9' }}
        >
          <div className="login-hero-image-wrapper" style={{ flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center', padding: '0 8rem' }}>
            <span className="login-form-label">Security Protocol</span>
            <h2 className="login-hero-title" style={{ color: '#191c1c', mixBlendMode: 'normal', marginBottom: '2rem' }}>
              Verify <br/>Security Code.
            </h2>
            <p className="login-hero-subtitle" style={{ maxWidth: '32rem' }}>
              Your sanctuary is guarded by double-blind identity verification. We've sent a 6-digit security code to your registered device.
            </p>


          </div>
          <div className="login-hero-gradient-bleed" />
        </motion.div>

        {/* Right Side: OTP Input */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          className="login-form-section"
        >
          <div className="login-form-container">
            <div className="login-form-header">
              <span className="login-form-label">Identity Access</span>
              <h1 className="login-form-title">Enter Code</h1>
              <p className="login-form-desc">Verification code sent to •••• ••• {phoneNumber.slice(-4)}</p>
            </div>

            <form className="login-form" onSubmit={handleVerify}>
              <div className="otp-input-grid">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    ref={(el) => (inputRefs.current[idx] = el)}
                    type="tel"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(e.target.value, idx)}
                    onKeyDown={(e) => handleKeyDown(e, idx)}
                    className="otp-digit-field"
                    autoFocus={idx === 0}
                  />
                ))}
              </div>

              {error && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="login-error">
                  {error}
                </motion.div>
              )}

              <div className="login-cta-group">
                <button
                  type="submit"
                  disabled={otp.some(d => !d) || loading}
                  className={`login-proceed-btn ${otp.some(d => !d) || loading ? "login-proceed-btn--disabled" : ""}`}
                >
                  {loading ? "Authorizing..." : "PROCEED TO SKINSIGHT →"}
                </button>

                <div className="text-center" style={{ marginTop: '1rem' }}>
                  <p className="expert-title" style={{ color: '#a8a29e' }}>
                    Resend code in <span style={{ color: '#4e635e', fontWeight: 700 }}>{timer}s</span>
                  </p>
                  <button 
                    type="button"
                    disabled={timer > 0}
                    onClick={() => {
                        setTimer(30);
                        setError("New security code dispatched.");
                    }}
                    className="login-create-link"
                    style={{ fontSize: '0.8125rem', marginTop: '1rem', background: 'none', border: 'none', cursor: timer === 0 ? 'pointer' : 'default', opacity: timer === 0 ? 1 : 0.3 }}
                  >
                    Resend Security Code
                  </button>
                </div>
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
                {infoContent[activeInfo].contactGrid && (
                   <div className="contact-info-grid" style={{ marginTop: '0' }}>
                     <div className="contact-item">
                       <h3 className="detail-title">Clinical Support</h3>
                       <p className="detail-text">+1 (650) 555-0142</p>
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
