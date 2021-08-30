import { createClient } from '@supabase/supabase-js'

const supabaseUrl: string = process.env.SUPABASE_URL || ''
const supabaseKey: string = process.env.SUPABASE_API || ''

export const supabase = createClient(supabaseUrl, supabaseKey)
