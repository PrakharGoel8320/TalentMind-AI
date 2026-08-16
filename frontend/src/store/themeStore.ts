'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
  setDark: (isDark: boolean) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: true,

      toggleTheme: () =>
        set((state) => ({
          isDark: !state.isDark,
        })),

      setDark: (isDark: boolean) =>
        set({
          isDark,
        }),
    }),
    {
      name: 'talentmind-theme',
    }
  )
);
