import { useTranslation } from '../utils/I18nProvider'
import { Box, Typography } from '@mui/material'

export default function PlaceholderPage({ titleKey }: { titleKey: string }) {
  const { t } = useTranslation()
  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t(titleKey)}</Typography>
      <Typography color="text.secondary">Module under development.</Typography>
    </Box>
  )
}



