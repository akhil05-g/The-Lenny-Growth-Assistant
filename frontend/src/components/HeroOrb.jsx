import React from 'react';
import { Mic } from 'lucide-react';

export default function HeroOrb() {
  return (
    <div className="flex flex-col items-center justify-center my-auto py-2 select-none pointer-events-none">
      {/* Title matching Dribbble reference */}
      <h1 className="text-xl md:text-2xl font-bold tracking-tight text-center mb-4">
        <span className="bg-gradient-to-r from-rose-400 to-pink-500 bg-clip-text text-transparent font-medium">
          AI Powers{' '}
        </span>
        <span className="text-slate-900 font-extrabold">
          Grounded Growth{' '}
        </span>
        <span className="text-slate-400 font-normal">
          And Voice Access
        </span>
      </h1>

      {/* 3D Glassy Orb element matching Dribbble wallpaper aesthetic */}
      <div className="flex flex-col items-center justify-center">
        <div className="glossy-orb-element">
          <div className="w-8 h-8 rounded-full bg-white/25 backdrop-blur-md flex items-center justify-center text-white/90 shadow-inner">
            <Mic className="w-3.5 h-3.5 opacity-80" />
          </div>
        </div>
        <div className="glossy-orb-reflection" />
      </div>
    </div>
  );
}
