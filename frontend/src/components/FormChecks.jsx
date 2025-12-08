import React, { useState } from 'react';
import { CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const FormChecks = ({ checks }) => {
  const [expanded, setExpanded] = useState(null);

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-200 mb-4">Biomechanical Analysis</h3>
      {checks.map((check, i) => (
        <div 
          key={i} 
          className={`rounded-xl border transition-all cursor-pointer ${
            check.is_error 
              ? 'bg-red-500/5 border-red-500/30 hover:bg-red-500/10' 
              : 'bg-green-500/5 border-green-500/30 hover:bg-green-500/10'
          }`}
          onClick={() => setExpanded(expanded === i ? null : i)}
        >
          <div className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {check.is_error ? (
                <XCircle className="w-5 h-5 text-red-400" />
              ) : (
                <CheckCircle2 className="w-5 h-5 text-green-400" />
              )}
              <span className="font-medium">{check.name}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-sm font-mono px-2 py-1 rounded ${
                check.is_error ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'
              }`}>
                {check.value}
              </span>
              {expanded === i ? <ChevronUp className="w-4 h-4 text-gray-500"/> : <ChevronDown className="w-4 h-4 text-gray-500"/>}
            </div>
          </div>

          <AnimatePresence>
            {expanded === i && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="px-4 pb-4 text-sm text-gray-400 border-t border-white/5 pt-3">
                  {check.is_error ? (
                    <p className="text-red-200"><strong className="text-red-400">Fix:</strong> {check.recommendation}</p>
                  ) : (
                    <p className="text-green-200">Excellent form maintained in this area.</p>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
};

export default FormChecks;