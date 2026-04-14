import { useState } from "react";
import { 
  CircleUser, 
  Image as ImageIcon, 
  FileText, 
  HelpCircle, 
  Shield, 
  LogOut,
  ChevronDown
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const handleLogout = () => {
    // Clear user identifying data (using the correct keys from login/otp pages)
    localStorage.removeItem("userPhone");
    localStorage.removeItem("isVerified");
    localStorage.removeItem("userDetails");
    localStorage.removeItem("userConcerns");
    localStorage.removeItem("onboarding_complete");
    // Redirect to landing/login
    router.push("/");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-stone-100 px-16 h-20 flex items-center justify-between font-['Plus_Jakarta_Sans',_sans-serif]">
      {/* Left: Branding */}
      <div className="flex items-center gap-1">
        <Link href="/" className="text-2xl font-black text-[#004d40] tracking-tighter">
          SkinSight
        </Link>
      </div>

      {/* Center: Navigation Links */}
      {!(pathname === "/" || pathname === "/welcome") && (
        <div className="flex items-center gap-12">
          <Link 
            href="/analysis" 
            className={`text-sm font-bold transition-all relative py-2 ${
              pathname === '/analysis' 
              ? 'text-[#004d40] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[#004d40] after:rounded-full' 
              : 'text-stone-400 hover:text-stone-600'
            }`}
          >
            Analysis
          </Link>
          <Link 
            href="/analysis/report" 
            className={`text-sm font-bold transition-all relative py-2 ${
              pathname?.includes('/analysis/report') 
              ? 'text-[#004d40] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[#004d40] after:rounded-full' 
              : 'text-stone-400 hover:text-stone-600'
            }`}
          >
            Report
          </Link>
          <Link 
            href="/treatments" 
            className={`text-sm font-bold transition-all relative py-2 ${
              pathname?.includes('/treatments') 
              ? 'text-[#004d40] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[#004d40] after:rounded-full' 
              : 'text-stone-400 hover:text-stone-600'
            }`}
          >
            Treatments
          </Link>
        </div>
      )}

      {/* Right: Actions */}
      <div className="flex items-center gap-6">
        {!(pathname === "/" || pathname === "/welcome") && (
          <div className="relative">
            <button 
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className={`flex items-center gap-1 transition-all ${
                isProfileOpen ? 'text-[#004d40]' : 'text-stone-400 hover:text-[#004d40]'
              }`}
            >
              <CircleUser className="w-6 h-6" />
              <ChevronDown className={`w-4 h-4 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} />
            </button>

            <AnimatePresence>
              {isProfileOpen && (
                <>
                  {/* Backdrop to close on click outside */}
                  <div 
                    className="fixed inset-0 z-[-1]" 
                    onClick={() => setIsProfileOpen(false)} 
                  />
                  
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 mt-4 w-64 bg-white border border-stone-100 rounded-2xl shadow-xl shadow-stone-200/50 overflow-hidden"
                  >
                    <div className="p-2">
                      <Link 
                        href="/profile/history?view=photos"
                        onClick={() => setIsProfileOpen(false)}
                        className="flex items-center gap-3 w-full p-3 text-sm font-medium text-stone-600 hover:bg-stone-50 hover:text-[#004d40] rounded-xl transition-all group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-stone-50 flex items-center justify-center group-hover:bg-[#004d40]/10">
                          <ImageIcon className="w-4 h-4" />
                        </div>
                        My Photos
                      </Link>

                      <Link 
                        href="/profile/history?view=reports"
                        onClick={() => setIsProfileOpen(false)}
                        className="flex items-center gap-3 w-full p-3 text-sm font-medium text-stone-600 hover:bg-stone-50 hover:text-[#004d40] rounded-xl transition-all group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-stone-50 flex items-center justify-center group-hover:bg-[#004d40]/10">
                          <FileText className="w-4 h-4" />
                        </div>
                        Report Section
                      </Link>

                      <div className="h-px bg-stone-100 my-1 mx-2" />

                      <Link 
                        href="/help"
                        onClick={() => setIsProfileOpen(false)}
                        className="flex items-center gap-3 w-full p-3 text-sm font-medium text-stone-600 hover:bg-stone-50 hover:text-[#004d40] rounded-xl transition-all group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-stone-50 flex items-center justify-center group-hover:bg-[#004d40]/10">
                          <HelpCircle className="w-4 h-4" />
                        </div>
                        Help
                      </Link>

                      <Link 
                        href="/policies"
                        onClick={() => setIsProfileOpen(false)}
                        className="flex items-center gap-3 w-full p-3 text-sm font-medium text-stone-600 hover:bg-stone-50 hover:text-[#004d40] rounded-xl transition-all group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-stone-50 flex items-center justify-center group-hover:bg-[#004d40]/10">
                          <Shield className="w-4 h-4" />
                        </div>
                        Policies
                      </Link>

                      <div className="h-px bg-stone-100 my-1 mx-2" />

                      <button 
                        onClick={handleLogout}
                        className="flex items-center gap-3 w-full p-3 text-sm font-semibold text-rose-500 hover:bg-rose-50 rounded-xl transition-all group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center group-hover:bg-rose-100">
                          <LogOut className="w-4 h-4" />
                        </div>
                        Logout
                      </button>
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </nav>
  );
}

