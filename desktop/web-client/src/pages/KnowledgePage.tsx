import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Trash2, Plus, Loader2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { sutraAPI, Concept } from '../api/client';

export function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: concepts, isLoading, error } = useQuery({
    queryKey: ['concepts'],
    queryFn: sutraAPI.listConcepts,
  });

  const deleteMutation = useMutation({
    mutationFn: sutraAPI.deleteConcept,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });

  const filteredConcepts = concepts?.filter((c) =>
    c.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-dark-700 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white">Knowledge Base</h1>
              <p className="text-dark-400 mt-1">
                {concepts?.length || 0} concepts stored
              </p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Concept
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search knowledge..."
              className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto">
          {isLoading && (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center space-y-2">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
                <p className="text-dark-400">Failed to load concepts</p>
              </div>
            </div>
          )}

          {filteredConcepts && filteredConcepts.length === 0 && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center space-y-2">
                <p className="text-dark-400">
                  {searchQuery ? 'No concepts match your search' : 'No concepts yet'}
                </p>
                {!searchQuery && (
                  <button
                    onClick={() => setShowAddModal(true)}
                    className="text-primary-500 hover:text-primary-400"
                  >
                    Add your first concept
                  </button>
                )}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {filteredConcepts?.map((concept) => (
                <ConceptCard
                  key={concept.concept_id}
                  concept={concept}
                  onDelete={() => deleteMutation.mutate(concept.concept_id)}
                  isDeleting={deleteMutation.isPending}
                />
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Add Modal */}
      <AddConceptModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
      />
    </div>
  );
}

function ConceptCard({
  concept,
  onDelete,
  isDeleting,
}: {
  concept: Concept;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="p-4 bg-dark-800 border border-dark-700 rounded-lg hover:border-primary-600 transition-colors group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        {concept.semantic_type && (
          <span className="px-2 py-1 text-xs font-medium bg-primary-600/20 text-primary-400 rounded">
            {concept.semantic_type}
          </span>
        )}
        <button
          onClick={onDelete}
          disabled={isDeleting}
          className="p-1 text-dark-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all disabled:opacity-50"
        >
          {isDeleting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Trash2 className="w-4 h-4" />
          )}
        </button>
      </div>
      <p className="text-dark-100 line-clamp-3">{concept.content}</p>
      {concept.confidence && (
        <div className="mt-3 flex items-center gap-2">
          <div className="flex-1 h-1.5 bg-dark-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all"
              style={{ width: `${concept.confidence * 100}%` }}
            />
          </div>
          <span className="text-xs text-dark-400">
            {(concept.confidence * 100).toFixed(0)}%
          </span>
        </div>
      )}
      {concept.created_at && (
        <p className="text-xs text-dark-500 mt-2">
          {new Date(concept.created_at).toLocaleDateString()}
        </p>
      )}
    </motion.div>
  );
}

function AddConceptModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [content, setContent] = useState('');
  const queryClient = useQueryClient();

  const learnMutation = useMutation({
    mutationFn: sutraAPI.learn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['concepts'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      setContent('');
      onClose();
    },
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-dark-900 rounded-lg shadow-xl max-w-lg w-full p-6"
      >
        <h2 className="text-2xl font-bold text-white mb-4">Add New Concept</h2>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Enter concept content..."
          rows={4}
          className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
        />
        <div className="flex gap-3 mt-4">
          <button
            onClick={onClose}
            disabled={learnMutation.isPending}
            className="flex-1 px-4 py-2 bg-dark-800 hover:bg-dark-700 rounded-lg font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => content.trim() && learnMutation.mutate(content.trim())}
            disabled={!content.trim() || learnMutation.isPending}
            className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
          >
            {learnMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Adding...
              </>
            ) : (
              'Add Concept'
            )}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
