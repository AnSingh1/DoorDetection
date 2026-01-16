"use client";

import React, { useState, useEffect, useRef, ReactNode, ChangeEvent, DragEvent } from 'react';
import { 
  Upload, 
  FileText, 
  Image as ImageIcon, 
  Trash2, 
  LayoutDashboard, 
  FolderOpen, 
  Settings, 
  CheckCircle,
  AlertCircle,
  File,
} from 'lucide-react';

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// --- Type Definitions ---
interface FileItem {
  id: string;
  name: string;
  size: number;
  type: string;
  object: File;
  date: Date;
}

interface Notification {
  message: string;
  type: 'success' | 'neutral';
}

interface DetectionBox {
  x: number;
  y: number;
  width: number;
  height: number;
  className: string;
  confidence: number;
}

interface DetectionImage {
  filename: string;
  image: string;
  original_image: string;
  boxes: DetectionBox[];
}

// --- Helper Functions ---
const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const getFileIcon = (type: string): ReactNode => {
  if (type.startsWith('image/')) return <ImageIcon className="w-8 h-8 text-purple-500" />;
  if (type === 'application/pdf') return <FileText className="w-8 h-8 text-red-500" />;
  return <File className="w-8 h-8 text-blue-500" />;
};

// --- Components ---

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const Sidebar = ({ activeTab, setActiveTab, isOpen, setIsOpen }: SidebarProps) => {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Overview' },
    { id: 'files', icon: FolderOpen, label: 'My Files' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      <div 
        className={`fixed inset-0 z-20 bg-black/50 transition-opacity lg:hidden ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={() => setIsOpen(false)}
      />

    </>
  );
};

const UploadZone = ({ onFilesAdded }: { onFilesAdded: (files: File[]) => void }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFilesAdded(Array.from(e.dataTransfer.files));
      e.dataTransfer.clearData();
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFilesAdded(Array.from(e.target.files));
    }
  };

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
      className={`relative group cursor-pointer flex flex-col items-center justify-center w-full h-64 rounded-2xl border-2 border-dashed transition-all duration-300 ease-out 
        ${isDragging 
          ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]' 
          : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-slate-50'
        }`}
    >
      <input
        type="file"
        multiple
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileInput}
        accept="image/*,.pdf"
      />
      
      <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4">
        <div className={`p-4 rounded-full mb-4 transition-colors ${isDragging ? 'bg-indigo-100' : 'bg-slate-100 group-hover:bg-indigo-50'}`}>
          <Upload className={`w-8 h-8 ${isDragging ? 'text-indigo-600' : 'text-slate-400 group-hover:text-indigo-500'}`} />
        </div>
        <p className="mb-2 text-lg font-medium text-slate-700">
          <span className="text-indigo-600">Click to upload</span> or drag and drop
        </p>
        <p className="text-sm text-slate-500 max-w-sm">
          Supports Images (JPG, PNG, GIF) and PDF Documents. 
          <br />You can also paste (Ctrl+V) directly anywhere on the page.
        </p>
      </div>
    </div>
  );
};

const FileCard = ({ file, onRemove }: { file: FileItem; onRemove: (id: string) => void }) => {
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file.object);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  return (
    <div className="group relative bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden flex flex-col">
      {/* Preview Area */}
      <div className="h-32 bg-slate-100 relative overflow-hidden flex items-center justify-center">
        {preview ? (
          <img src={preview} alt={file.name} className="w-full h-full object-cover" />
        ) : (
          <div className="transform transition-transform group-hover:scale-110 duration-300">
            {getFileIcon(file.type)}
          </div>
        )}
        
        {/* Overlay Actions */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button 
            onClick={() => onRemove(file.id)}
            className="p-2 bg-white rounded-full text-red-500 hover:bg-red-50 transition-colors"
            title="Delete file"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Info Area */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between">
            <h3 className="text-sm font-semibold text-slate-900 truncate pr-2" title={file.name}>
              {file.name}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1">{formatBytes(file.size)}</p>
        </div>
        
        <div className="mt-3 flex items-center justify-between">
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-slate-100 text-slate-600">
              {file.type.split('/')[1]?.toUpperCase() || 'FILE'}
            </span>
            <span className="text-xs text-slate-400">
                Just now
            </span>
        </div>
      </div>
    </div>
  );
};

interface BoundingBoxRendererProps {
  imageUrl: string;
  boxes: DetectionBox[];
  filename: string;
}

const BoundingBoxRenderer = ({ imageUrl, boxes, filename }: BoundingBoxRendererProps) => {
  const [imageSize, setImageSize] = useState<{ width: number; height: number } | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setImageSize({
      width: img.naturalWidth,
      height: img.naturalHeight
    });
  };

  // Calculate display dimensions and scale factor
  const getScaledDimensions = () => {
    if (!imageSize || !imgRef.current || !containerRef.current) return null;

    const container = containerRef.current.getBoundingClientRect();
    const maxWidth = container.width;
    const maxHeight = container.height;

    let displayWidth = imageSize.width;
    let displayHeight = imageSize.height;

    const widthRatio = maxWidth / displayWidth;
    const heightRatio = maxHeight / displayHeight;
    const ratio = Math.min(widthRatio, heightRatio, 1); // Don't scale up

    displayWidth *= ratio;
    displayHeight *= ratio;

    return {
      displayWidth,
      displayHeight,
      scaleX: displayWidth / imageSize.width,
      scaleY: displayHeight / imageSize.height
    };
  };

  const scaled = getScaledDimensions();

  return (
    <div ref={containerRef} className="relative w-full h-full flex items-center justify-center">
      <div className="relative" style={{ 
        width: scaled?.displayWidth, 
        height: scaled?.displayHeight 
      }}>
        <img 
          ref={imgRef}
          src={imageUrl} 
          alt={filename} 
          onLoad={handleImageLoad}
          className="w-full h-full object-contain"
        />
        
        {/* SVG Overlay for Bounding Boxes */}
        {scaled && (
          <svg 
            className="absolute inset-0 w-full h-full"
            viewBox={`0 0 ${imageSize?.width} ${imageSize?.height}`}
            preserveAspectRatio="xMidYMid meet"
          >
            {boxes.map((box, idx) => (
              <g key={idx}>
                {/* Rectangle */}
                <rect
                  x={box.x}
                  y={box.y}
                  width={box.width}
                  height={box.height}
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="3"
                  vectorEffect="non-scaling-stroke"
                />
                
                {/* Label Background */}
                <rect
                  x={box.x}
                  y={Math.max(0, box.y - 25)}
                  width={Math.max(80, box.width / 2)}
                  height="24"
                  fill="#10b981"
                  vectorEffect="non-scaling-stroke"
                />
                
                {/* Label Text */}
                <text
                  x={box.x + 4}
                  y={Math.max(20, box.y - 5)}
                  fill="white"
                  fontSize="14"
                  fontWeight="bold"
                  fontFamily="monospace"
                  vectorEffect="non-scaling-stroke"
                >
                  {box.className} {(box.confidence * 100).toFixed(0)}%
                </text>
              </g>
            ))}
          </svg>
        )}
      </div>
    </div>
  );
};

// --- Main App Component ---

const App = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notification, setNotification] = useState<Notification | null>(null);
  const [detectImages, setDetectImages] = useState<DetectionImage[]>([]);
  const [isDetecting, setIsDetecting] = useState(false);
  const [fullscreenImage, setFullscreenImage] = useState<DetectionImage | null>(null);
  const [showAnnotations, setShowAnnotations] = useState(true);

  // Global Paste Handler
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      if (e.clipboardData && e.clipboardData.files.length > 0) {
        e.preventDefault();
        const pastedFiles = Array.from(e.clipboardData.files);
        processFiles(pastedFiles);
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  const processFiles = (newFiles: File[]) => {
    const processed: FileItem[] = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type || 'unknown',
      object: file,
      date: new Date()
    }));

    setFiles(prev => [...processed, ...prev]);
    showNotification(`${processed.length} file(s) added successfully`, 'success');
  };

  const handleRemoveFile = (id: string) => {
    setFiles(files.filter(f => f.id !== id));
    showNotification('File removed', 'neutral');
  };

  const showNotification = (message: string, type: 'success' | 'neutral' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleDetect = async () => {
    if (files.length === 0) {
      showNotification('Please upload files first', 'neutral');
      return;
    }

    setIsDetecting(true);
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file.object);
    });

    try {
      const response = await fetch(`${API_URL}/detect`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Detection failed');

      const data = await response.json();
      if (data.images) {
        setDetectImages(data.images);
        showNotification('Detection complete!', 'success');
      } else {
        showNotification('No results returned', 'neutral');
      }
    } catch (error) {
      console.error('Error:', error);
      showNotification('Detection failed', 'neutral');
    } finally {
      setIsDetecting(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      {/* Toast Notification */}
      <div className={`fixed top-4 right-4 z-50 transition-all duration-300 transform ${notification ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0 pointer-events-none'}`}>
        <div className={`flex items-center px-4 py-3 rounded-lg shadow-lg border ${
          notification?.type === 'success' ? 'bg-white border-green-100 text-green-800' : 'bg-white border-slate-200 text-slate-800'
        }`}>
          {notification?.type === 'success' ? <CheckCircle className="w-5 h-5 mr-2 text-green-500" /> : <AlertCircle className="w-5 h-5 mr-2 text-slate-500" />}
          <span className="text-sm font-medium">{notification?.message}</span>
        </div>
      </div>

      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isOpen={sidebarOpen} 
        setIsOpen={setSidebarOpen} 
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Header */}
        

        {/* Scrollable Content Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                
                {/* Upload Section */}
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-slate-800">Quick Upload</h2>
                    </div>
                    <UploadZone onFilesAdded={processFiles} />
                    {files.length > 0 && (
                      <div className="mt-6 flex gap-4">
                        <button
                          onClick={handleDetect}
                          disabled={isDetecting}
                          className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed transition-colors"
                        >
                          {isDetecting ? 'Detecting...' : 'Detect'}
                        </button>
                      </div>
                    )}
                </section>

                {/* Recent Files Section */}
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-slate-800">
                          {files.length > 0 ? 'Recent Uploads' : 'No files yet'}
                        </h2>
                        {files.length > 0 && (
                          <button 
                            onClick={() => setFiles([])}
                            className="text-sm text-red-500 hover:text-red-600 font-medium hover:underline"
                          >
                            Clear All
                          </button>
                        )}
                    </div>

                    {files.length === 0 ? (
                        <div className="text-center py-12 bg-white rounded-xl border border-slate-200 border-dashed">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-50 mb-4">
                                <File className="w-8 h-8 text-slate-300" />
                            </div>
                            <h3 className="text-slate-900 font-medium">No files uploaded</h3>
                            <p className="text-slate-500 text-sm mt-1">Upload files to see them here.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {files.map(file => (
                                <FileCard key={file.id} file={file} onRemove={handleRemoveFile} />
                            ))}
                        </div>
                    )}
                </section>

                {/* Detection Result Section */}
                {detectImages.length > 0 && (
                  <section>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-slate-800">Detection Results ({detectImages.length})</h2>
                        <button
                          onClick={() => setDetectImages([])}
                          className="text-sm text-slate-500 hover:text-slate-700 font-medium"
                        >
                          Clear
                        </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {detectImages.map((item, index) => (
                        <div key={index} className="bg-white rounded-xl border border-slate-200 p-4 overflow-hidden relative group">
                          <h3 className="text-sm font-semibold text-slate-900 mb-3 truncate" title={item.filename}>
                            {item.filename}
                          </h3>
                          <div className="bg-slate-50 rounded-lg overflow-hidden relative">
                            <img src={item.image} alt={item.filename} className="w-full h-auto" />
                            <button
                              onClick={() => setFullscreenImage(item)}
                              className="absolute top-2 right-2 p-2 bg-white rounded-lg shadow-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-100"
                              title="Expand to fullscreen"
                            >
                              <svg
                                viewBox="0 0 1024 1024"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="#000"
                                width={24}
                                height={24}
                              >
                                <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                                <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g>
                                <g id="SVGRepo_iconCarrier">
                                  <path
                                    fill="#000"
                                    d="m160 96.064 192 .192a32 32 0 0 1 0 64l-192-.192V352a32 32 0 0 1-64 0V96h64v.064zm0 831.872V928H96V672a32 32 0 1 1 64 0v191.936l192-.192a32 32 0 1 1 0 64l-192 .192zM864 96.064V96h64v256a32 32 0 1 1-64 0V160.064l-192 .192a32 32 0 1 1 0-64l192-.192zm0 831.872-192-.192a32 32 0 0 1 0-64l192 .192V672a32 32 0 1 1 64 0v256h-64v-.064z"
                                  />
                                </g>
                              </svg>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* Fullscreen Modal */}
                {fullscreenImage && (
                  <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4" onClick={() => setFullscreenImage(null)}>
                    <div className="relative max-w-7xl max-h-[90vh] w-full h-full flex flex-col" onClick={(e) => e.stopPropagation()}>
                      {/* Top Controls */}
                      <div className="flex items-center justify-between mb-4 relative z-10">
                        <button
                          onClick={() => setShowAnnotations(!showAnnotations)}
                          className="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                          title={showAnnotations ? "Hide annotations" : "Show annotations"}
                        >
                          {showAnnotations ? "Hide" : "Show"} Annotations
                        </button>
                        <button
                          onClick={() => setFullscreenImage(null)}
                          className="p-2 bg-white rounded-full shadow-lg hover:bg-slate-100 transition-colors"
                          title="Close fullscreen"
                        >
                          <svg className="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>

                      {/* Image Container */}
                      <div className="flex-1 flex items-center justify-center overflow-hidden relative bg-black rounded-lg">
                        <div className="relative w-full h-full flex items-center justify-center">
                          {showAnnotations ? (
                            <img 
                              src={fullscreenImage.image} 
                              alt={fullscreenImage.filename} 
                              className="max-w-full max-h-full object-contain"
                            />
                          ) : (
                            <BoundingBoxRenderer 
                              imageUrl={fullscreenImage.original_image} 
                              boxes={fullscreenImage.boxes}
                              filename={fullscreenImage.filename}
                            />
                          )}
                        </div>
                      </div>

                      {/* Image Info */}
                      <div className="mt-4 text-center text-white">
                        <p className="text-lg font-semibold">{fullscreenImage.filename}</p>
                        {showAnnotations && fullscreenImage.boxes && (
                          <p className="text-sm text-gray-300 mt-1">
                            Detected: {fullscreenImage.boxes.length} door{fullscreenImage.boxes.length !== 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
            </div>
        </main>
      </div>
    </div>
  );
};

export default App;