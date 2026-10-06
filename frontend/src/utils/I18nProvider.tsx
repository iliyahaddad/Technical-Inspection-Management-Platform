import { createContext, useContext, useMemo, useState } from 'react'
import { getLocale, setLocale as applyLocale, t } from './i18n'

type Ctx = { t: typeof t; locale: 'en' | 'fa'; setLocale: (l: 'en' | 'fa') => void }
const I18nContext = createContext<Ctx>({ t, locale: 'fa', setLocale: () => undefined })

export function useTranslation() {
  return useContext(I18nContext)
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState(getLocale())
  const value = useMemo<Ctx>(
    () => ({ t, locale, setLocale: (l) => { applyLocale(l); setLocaleState(l) } }),
    [locale],
  )
  applyLocale(locale)
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}
