"use client";

import { useState } from "react";

interface Props {
  accept: string;
  label: string;
  onFile: (file: File) => void;
}

export default function FileDrop({ accept, label, onFile }: Props) {
  const [drag, setDrag] = useState(false);
  return (
    <label
      className={`dropzone ${drag ? "drag" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        if (e.dataTransfer.files?.[0]) onFile(e.dataTransfer.files[0]);
      }}
    >
      {label}
      <input
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
    </label>
  );
}
