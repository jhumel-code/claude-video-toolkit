// Font loading as a component (delayRender must run inside render context, not at module load).
import React, { useEffect, useState } from 'react';
import { staticFile, delayRender, continueRender } from 'remotion';

let cssInjected = false;
function injectCss() {
  if (cssInjected || typeof document === 'undefined') return;
  cssInjected = true;
  const s = document.createElement('style');
  s.textContent =
    "@font-face{font-family:'Geist';src:url('" + staticFile('fonts/Geist.ttf') + "');font-weight:100 900;}" +
    "@font-face{font-family:'GeistMono';src:url('" + staticFile('fonts/GeistMono.ttf') + "');}" +
    "@font-face{font-family:'InstrumentSerif';src:url('" + staticFile('fonts/InstrumentSerif-Regular.ttf') + "');}" +
    "@font-face{font-family:'InstrumentSerif';src:url('" + staticFile('fonts/InstrumentSerif-Italic.ttf') + "');font-style:italic;}";
  document.head.appendChild(s);
}

export const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    injectCss();
    Promise.all([
      document.fonts.load('600 16px "Geist"'),
      document.fonts.load('16px "GeistMono"'),
      document.fonts.load('40px "InstrumentSerif"'),
      document.fonts.load('italic 16px "InstrumentSerif"'),
    ]).then(() => continueRender(handle)).catch(() => continueRender(handle));
  }, [handle]);
  return null;
};
