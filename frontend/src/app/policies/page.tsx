"use client";

import { Shield, ArrowLeft, Lock, FileText, Globe } from "lucide-react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function PoliciesPage() {
  return (
    <div className="min-h-screen bg-stone-50 font-['Plus_Jakarta_Sans',_sans-serif]">
      <Navbar />
      
      <main className="pt-32 pb-20 px-16 max-w-4xl mx-auto">
        <Link 
          href="/analysis" 
          className="inline-flex items-center gap-2 text-stone-400 hover:text-[#004d40] transition-colors mb-8 text-sm font-bold group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to Dashboard
        </Link>
        
        <div className="bg-white p-12 rounded-[3rem] border border-stone-100 shadow-xl shadow-stone-200/20">
          <div className="w-16 h-16 bg-[#004d40]/5 rounded-2xl flex items-center justify-center text-[#004d40] mb-8">
            <Shield className="w-8 h-8" />
          </div>
          
          <h1 className="text-4xl font-black text-[#004d40] tracking-tight mb-4">
            Legal & Privacy Policies
          </h1>
          <p className="text-stone-500 font-medium mb-12">
            Last updated: April 11, 2026. Please read our terms and privacy commitments carefully.
          </p>
          
          <div className="space-y-12">
            <section>
              <div className="flex items-center gap-3 mb-4 text-[#004d40]">
                <Lock className="w-5 h-5" />
                <h2 className="text-xl font-bold">Privacy Policy</h2>
              </div>
              <p className="text-stone-500 leading-relaxed mb-4">
                Your skin data is sensitive medical information. We collect and process your facial scans solely to provide you with health insights and tracking progress. We do not sell your personal images to third parties.
              </p>
              <ul className="list-disc list-inside text-stone-500 space-y-2 ml-4">
                <li>End-to-end encryption for all image data.</li>
                <li>Local processing for anatomical landmark detection.</li>
                <li>Option to delete your entire history at any time.</li>
              </ul>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-4 text-[#004d40]">
                <FileText className="w-5 h-5" />
                <h2 className="text-xl font-bold">Terms of Use</h2>
              </div>
              <p className="text-stone-500 leading-relaxed">
                SkinSight is an AI-powered screening tool and not a replacement for professional medical diagnosis. By using this service, you acknowledge that recommendations are for informational purposes.
              </p>
            </section>

            <section>
              <div className="flex items-center gap-3 mb-4 text-[#004d40]">
                <Globe className="w-5 h-5" />
                <h2 className="text-xl font-bold">Cookies</h2>
              </div>
              <p className="text-stone-500 leading-relaxed">
                We use essential session cookies to keep you logged in and ensure a seamless experience. We do not use tracking cookies for advertising.
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
