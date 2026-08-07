/**
 * Image → base64 helper for the agent's OCR input.
 *
 * The agent endpoint accepts `image_base64` as a raw base64 string
 * (`app/core/rag/ocr.py` does a bare `base64.b64decode`), so the
 * `data:image/...;base64,` prefix from `readAsDataURL` must be stripped.
 * Large images are downscaled on a canvas so the JSON payload stays small,
 * while small images are kept at full resolution (higher detail helps OCR).
 */

const MAX_DIMENSION = 2048;
const MAX_BYTES = 2 * 1024 * 1024; // 2 MB

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error || new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}

/**
 * Downscale an image file on a canvas, returning a compressed data URL.
 * Falls back to the original data URL if canvas processing fails.
 */
function downscale(dataUrl, maxDim) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      try {
        const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
        if (scale >= 1) return resolve(dataUrl); // already small enough

        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.85));
      } catch {
        resolve(dataUrl);
      }
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

/**
 * Read an image file into { base64, dataUrl, name }.
 *
 * @param {File} file
 * @param {Object} [opts]        - { maxDim, maxBytes }
 * @returns {Promise<{base64: string, dataUrl: string, name: string}>}
 */
export async function fileToImageData(file, opts = {}) {
  const maxDim = opts.maxDim ?? MAX_DIMENSION;
  const maxBytes = opts.maxBytes ?? MAX_BYTES;

  let dataUrl = await readAsDataURL(file);

  // Downscale only genuinely large images (payload bound); keep small
  // images untouched so OCR gets maximum resolution.
  if (file.size > maxBytes) {
    dataUrl = await downscale(dataUrl, maxDim);
  }

  // Strip the `data:image/<type>;base64,` prefix → raw base64 for the backend.
  const commaIdx = dataUrl.indexOf(",");
  const base64 = commaIdx >= 0 ? dataUrl.slice(commaIdx + 1) : dataUrl;

  return { base64, dataUrl, name: file.name };
}
