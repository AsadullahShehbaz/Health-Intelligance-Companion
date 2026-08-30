/**
 * PDF → base64 helper for the agent's document-OCR input.
 * Same contract as image.js: strips the data-URI prefix, backend expects
 * a raw base64 string. No client-side downscaling (that's an image-only
 * concept) — just a hard size check with a clear error the caller can
 * surface to the user.
 */

const MAX_PDF_BYTES = 10 * 1024 * 1024; // keep in sync with backend PDF_MAX_SIZE_MB

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error || new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}

export async function fileToPdfData(file, opts = {}) {
  const maxBytes = opts.maxBytes ?? MAX_PDF_BYTES;
  if (file.size > maxBytes) {
    throw new Error(`PDF is too large (max ${Math.round(maxBytes / (1024 * 1024))} MB).`);
  }

  const dataUrl = await readAsDataURL(file);
  const commaIdx = dataUrl.indexOf(",");
  const base64 = commaIdx >= 0 ? dataUrl.slice(commaIdx + 1) : dataUrl;
  return { base64, name: file.name };
}
