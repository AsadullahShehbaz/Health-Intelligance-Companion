import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    rules: {
      // react-refresh v0.5 doesn't auto-allow `use*` hooks exported alongside
      // components — the react-refresh/vite preset only sets allowConstantExport.
      // AuthContext exports useAuth() (a hook) next to AuthProvider, and
      // ConversationsContext exports useConversations() next to
      // ConversationsProvider, so allow both.
      'react-refresh/only-export-components': [
        'error',
        { allowConstantExport: true, allowExportNames: ['useAuth', 'useConversations'] },
      ],
    },
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
])
