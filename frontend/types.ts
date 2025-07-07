// frontend/types.ts

/**
 * Represents an insurance document in your app.
 */
export interface Document {
    id: number;
    filename: string;
    s3_key: string;
    extracted_text?: string;
    department?: string;
    category?: string;
    subcategory?: string;
    summary?: string;
    action_items?: string;
    status: string;
    destination_bucket?: string;
    destination_key?: string;
    error_message?: string;
    email_error?: string;
  
    // ── NEW METADATA FIELDS ──
    account_number?: string;
    policyholder_name?: string;
    policy_number?: string;
    claim_number?: string;
  
    created_at: string;
    updated_at?: string;
  }
  