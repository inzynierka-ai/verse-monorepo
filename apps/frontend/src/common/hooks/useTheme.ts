import { useCallback } from 'react';

interface HslColor {
  h: number;
  s: number;
  l: number;
}

interface ThemeColors {
  // HSL components for base colors
  primaryH: number;
  primaryS: number;
  primaryL: number;
  
  accentH: number;
  accentS: number;
  accentL: number;
  
  secondaryAccentH: number;
  secondaryAccentS: number;
  secondaryAccentL: number;
  
  darkBgH: number;
  darkBgS: number;
  darkBgL: number;
  
  lightTextH: number;
  lightTextS: number;
  lightTextL: number;
  
  errorH: number;
  errorS: number;
  errorL: number;
  
  successH: number;
  successS: number;
  successL: number;
}

type LocationTheme = 'library' | 'forest' | 'castle' | 'cave' | 'beach' | 'space';

// Convert hex to HSL components
const hexToHsl = (hex: string): HslColor => {
  // Remove the # if present
  hex = hex.replace(/^#/, '');
  
  // Parse the hex components
  let r = parseInt(hex.slice(0, 2), 16) / 255;
  let g = parseInt(hex.slice(2, 4), 16) / 255;
  let b = parseInt(hex.slice(4, 6), 16) / 255;
  
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  let l = (max + min) / 2;
  
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    
    h /= 6;
  }
  
  return { 
    h: Math.round(h * 360), 
    s: Math.round(s * 100), 
    l: Math.round(l * 100) 
  };
};

// Predefined color palettes based on location themes
const themes: Record<LocationTheme, ThemeColors> = {
  library: {
    primaryH: 26, primaryS: 62, primaryL: 29,
    accentH: 39, accentS: 53, accentL: 52,
    secondaryAccentH: 35, secondaryAccentS: 56, secondaryAccentL: 74,
    darkBgH: 26, darkBgS: 51, darkBgL: 12,
    lightTextH: 35, lightTextS: 56, lightTextL: 90,
    errorH: 0, errorS: 54, errorL: 42,
    successH: 140, successS: 24, successL: 34
  },
  forest: {
    primaryH: 121, primaryS: 36, primaryL: 27,
    accentH: 90, accentS: 35, accentL: 56,
    secondaryAccentH: 120, secondaryAccentS: 38, secondaryAccentL: 85,
    darkBgH: 120, darkBgS: 28, darkBgL: 8,
    lightTextH: 90, lightTextS: 60, lightTextL: 95,
    errorH: 0, errorS: 54, errorL: 42,
    successH: 140, successS: 24, successL: 34
  },
  castle: {
    primaryH: 240, primaryS: 17, primaryL: 35,
    accentH: 315, accentS: 8, accentL: 60,
    secondaryAccentH: 9, secondaryAccentS: 20, secondaryAccentL: 72,
    darkBgH: 240, darkBgS: 26, darkBgL: 18,
    lightTextH: 20, lightTextS: 24, lightTextL: 92,
    errorH: 0, errorS: 54, errorL: 42,
    successH: 140, successS: 24, successL: 34
  },
  cave: {
    primaryH: 213, primaryS: 30, primaryL: 32,
    accentH: 179, accentS: 51, accentL: 56,
    secondaryAccentH: 168, secondaryAccentS: 100, secondaryAccentL: 72,
    darkBgH: 222, darkBgS: 59, darkBgL: 11,
    lightTextH: 204, lightTextS: 28, lightTextL: 95,
    errorH: 0, errorS: 54, errorL: 42,
    successH: 140, successS: 24, successL: 34
  },
  beach: {
    primaryH: 196, primaryS: 76, primaryL: 41,
    accentH: 43, accentS: 100, accentL: 70,
    secondaryAccentH: 38, secondaryAccentS: 73, secondaryAccentL: 80,
    darkBgH: 196, darkBgS: 76, darkBgL: 16,
    lightTextH: 210, lightTextS: 60, lightTextL: 98,
    errorH: 0, errorS: 54, errorL: 42,
    successH: 140, successS: 24, successL: 34
  },
  space: {
    primaryH: 271, primaryS: 63, primaryL: 46,
    accentH: 276, accentS: 100, accentL: 83,
    secondaryAccentH: 261, secondaryAccentS: 100, secondaryAccentL: 86,
    darkBgH: 273, darkBgS: 100, darkBgL: 14,
    lightTextH: 210, lightTextS: 20, lightTextL: 98,
    errorH: 0, errorS: 54, errorL: 42,
    successH: 140, successS: 24, successL: 34
  }
};

// Custom hook for theme management
export const useTheme = () => {
  // Apply theme based on location
  const applyTheme = useCallback((themeName: LocationTheme) => {
    console.log(themeName)
    const theme = themes[themeName];
    if (!theme) return;

    // Update HSL base variables
    document.documentElement.style.setProperty('--primary-h', theme.primaryH.toString());
    document.documentElement.style.setProperty('--primary-s', `${theme.primaryS}%`);
    document.documentElement.style.setProperty('--primary-l', `${theme.primaryL}%`);
    
    document.documentElement.style.setProperty('--accent-h', theme.accentH.toString());
    document.documentElement.style.setProperty('--accent-s', `${theme.accentS}%`);
    document.documentElement.style.setProperty('--accent-l', `${theme.accentL}%`);
    
    document.documentElement.style.setProperty('--secondary-accent-h', theme.secondaryAccentH.toString());
    document.documentElement.style.setProperty('--secondary-accent-s', `${theme.secondaryAccentS}%`);
    document.documentElement.style.setProperty('--secondary-accent-l', `${theme.secondaryAccentL}%`);
    
    document.documentElement.style.setProperty('--dark-bg-h', theme.darkBgH.toString());
    document.documentElement.style.setProperty('--dark-bg-s', `${theme.darkBgS}%`);
    document.documentElement.style.setProperty('--dark-bg-l', `${theme.darkBgL}%`);
    
    document.documentElement.style.setProperty('--light-text-h', theme.lightTextH.toString());
    document.documentElement.style.setProperty('--light-text-s', `${theme.lightTextS}%`);
    document.documentElement.style.setProperty('--light-text-l', `${theme.lightTextL}%`);
    
    document.documentElement.style.setProperty('--error-h', theme.errorH.toString());
    document.documentElement.style.setProperty('--error-s', `${theme.errorS}%`);
    document.documentElement.style.setProperty('--error-l', `${theme.errorL}%`);
    
    document.documentElement.style.setProperty('--success-h', theme.successH.toString());
    document.documentElement.style.setProperty('--success-s', `${theme.successS}%`);
    document.documentElement.style.setProperty('--success-l', `${theme.successL}%`);
    
    // All the derived colors will update automatically thanks to HSL and calc()
  }, []);

  // Apply custom theme with specific colors in hex format
  const applyCustomTheme = useCallback((colors: Record<string, string>) => {
    if (colors.primaryColor) {
      const hsl = hexToHsl(colors.primaryColor);
      document.documentElement.style.setProperty('--primary-h', hsl.h.toString());
      document.documentElement.style.setProperty('--primary-s', `${hsl.s}%`);
      document.documentElement.style.setProperty('--primary-l', `${hsl.l}%`);
    }
    
    if (colors.accentColor) {
      const hsl = hexToHsl(colors.accentColor);
      document.documentElement.style.setProperty('--accent-h', hsl.h.toString());
      document.documentElement.style.setProperty('--accent-s', `${hsl.s}%`);
      document.documentElement.style.setProperty('--accent-l', `${hsl.l}%`);
    }
    
    if (colors.secondaryAccent) {
      const hsl = hexToHsl(colors.secondaryAccent);
      document.documentElement.style.setProperty('--secondary-accent-h', hsl.h.toString());
      document.documentElement.style.setProperty('--secondary-accent-s', `${hsl.s}%`);
      document.documentElement.style.setProperty('--secondary-accent-l', `${hsl.l}%`);
    }
    
    if (colors.darkBg) {
      const hsl = hexToHsl(colors.darkBg);
      document.documentElement.style.setProperty('--dark-bg-h', hsl.h.toString());
      document.documentElement.style.setProperty('--dark-bg-s', `${hsl.s}%`);
      document.documentElement.style.setProperty('--dark-bg-l', `${hsl.l}%`);
    }
    
    if (colors.lightText) {
      const hsl = hexToHsl(colors.lightText);
      document.documentElement.style.setProperty('--light-text-h', hsl.h.toString());
      document.documentElement.style.setProperty('--light-text-s', `${hsl.s}%`);
      document.documentElement.style.setProperty('--light-text-l', `${hsl.l}%`);
    }
  }, []);

  // Adjust theme brightness (useful for user preferences or time-of-day adjustments)
  const adjustBrightness = useCallback((factor: number) => {
    // Adjust the lightness of all colors
    // Factor > 1 brightens, < 1 darkens
    document.documentElement.style.setProperty('--primary-l-adjust', `${factor}`);
    document.documentElement.style.setProperty('--accent-l-adjust', `${factor}`);
    document.documentElement.style.setProperty('--dark-bg-l-adjust', `${factor}`);
  }, []);

  return { applyTheme, applyCustomTheme, adjustBrightness, themes };
};

// Function to extract dominant colors from an image URL
export const extractColorsFromImage = async (imageUrl: string): Promise<Record<string, string>> => {
  // This is a placeholder - in a real app, you'd use a color extraction library
  // like color-thief or a backend API for this functionality
  
  // For demo purposes, return random colors based on the URL hash
  const hash = Array.from(imageUrl).reduce((h, c) => (h + c.charCodeAt(0)) % 360, 0);
  
  return {
    primaryColor: `hsl(${hash}, 60%, 30%)`,
    accentColor: `hsl(${(hash + 30) % 360}, 70%, 60%)`,
    secondaryAccent: `hsl(${(hash + 60) % 360}, 60%, 75%)`,
    darkBg: `hsl(${hash}, 70%, 10%)`,
    lightText: `hsl(${(hash + 10) % 360}, 30%, 95%)`,
  };
}; 