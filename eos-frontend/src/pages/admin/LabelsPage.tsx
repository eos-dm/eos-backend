/**
 * EOS Platform - Labels Admin Page
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { labelsApi } from '@/services/api';
import type { LabelDefinition, LabelValue, LabelType } from '@/types';
import {
  PlusIcon,
  TagIcon,
  PencilIcon,
  TrashIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

// Label Type colors
const typeColors: Record<LabelType, string> = {
  single: 'bg-blue-100 text-blue-700',
  multiple: 'bg-green-100 text-green-700',
  hierarchical: 'bg-purple-100 text-purple-700',
};

// Max labels warning threshold
const MAX_LABELS = 20;

// Create Label Modal
interface LabelModalProps {
  isOpen: boolean;
  onClose: () => void;
  label?: LabelDefinition | null;
  currentCount: number;
}

function LabelModal({ isOpen, onClose, label, currentCount }: LabelModalProps) {
  const queryClient = useQueryClient();
  const isEditing = !!label;
  const [formData, setFormData] = useState({
    name: label?.name || '',
    code: label?.code || '',
    description: label?.description || '',
    label_type: label?.label_type || 'single' as LabelType,
    is_hierarchical: label?.is_hierarchical ?? false,
    max_levels: label?.max_levels || 3,
    is_required: label?.is_required ?? false,
    is_active: label?.is_active ?? true,
    display_order: label?.display_order || currentCount + 1,
  });
  const [error, setError] = useState('');

  const createMutation = useMutation({
    mutationFn: labelsApi.createLabelDefinition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['label-definitions'] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || err.response?.data?.non_field_errors?.[0] || 'Failed to create label');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<LabelDefinition>) => labelsApi.updateLabelDefinition(label!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['label-definitions'] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update label');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!isEditing && currentCount >= MAX_LABELS) {
      setError(`Maximum of ${MAX_LABELS} labels allowed per tenant`);
      return;
    }

    const data = {
      name: formData.name,
      code: formData.code,
      description: formData.description || undefined,
      label_type: formData.label_type,
      is_hierarchical: formData.is_hierarchical,
      max_levels: formData.max_levels,
      is_required: formData.is_required,
      is_active: formData.is_active,
      display_order: formData.display_order,
    };

    if (isEditing) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-xl shadow-xl max-w-lg w-full p-6 text-left">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {isEditing ? 'Edit Label Definition' : 'Create New Label Definition'}
          </h3>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="input"
                  placeholder="Product Category"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Code</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  required
                  className="input"
                  placeholder="product_category"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="input"
                placeholder="Label description..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={formData.label_type}
                  onChange={(e) => setFormData({ ...formData, label_type: e.target.value as LabelType })}
                  className="input"
                >
                  <option value="single">Single Select</option>
                  <option value="multiple">Multiple Select</option>
                  <option value="hierarchical">Hierarchical</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
                <input
                  type="number"
                  value={formData.display_order}
                  onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) })}
                  min="1"
                  className="input"
                />
              </div>
            </div>

            {formData.label_type === 'hierarchical' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Levels</label>
                <input
                  type="number"
                  value={formData.max_levels}
                  onChange={(e) => setFormData({ ...formData, max_levels: parseInt(e.target.value) })}
                  min="1"
                  max="10"
                  className="input w-24"
                />
              </div>
            )}

            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_required"
                  checked={formData.is_required}
                  onChange={(e) => setFormData({ ...formData, is_required: e.target.checked })}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="is_required" className="ml-2 block text-sm text-gray-700">
                  Required
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                  Active
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button type="button" onClick={onClose} className="btn btn-secondary">
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="btn btn-primary"
              >
                {createMutation.isPending || updateMutation.isPending
                  ? 'Saving...'
                  : isEditing
                  ? 'Update Label'
                  : 'Create Label'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Label Values Tree Component
function LabelValueTree({ definition }: { definition: LabelDefinition }) {
  const [expanded, setExpanded] = useState(false);
  const { data: valuesData, isLoading } = useQuery({
    queryKey: ['label-values', definition.id],
    queryFn: () => labelsApi.getLabelValueTree(definition.id),
    enabled: expanded,
  });

  const values = valuesData || [];

  const renderValue = (value: LabelValue, depth = 0) => (
    <div key={value.id} style={{ paddingLeft: `${depth * 20}px` }} className="py-1">
      <span className="text-sm text-gray-700">
        {value.name}
        {!value.is_active && <span className="text-gray-400 ml-2">(inactive)</span>}
      </span>
      {value.children?.map((child) => renderValue(child, depth + 1))}
    </div>
  );

  return (
    <div className="mt-4 pt-4 border-t border-gray-100">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center text-sm text-gray-600 hover:text-gray-900"
      >
        {expanded ? (
          <ChevronDownIcon className="h-4 w-4 mr-1" />
        ) : (
          <ChevronRightIcon className="h-4 w-4 mr-1" />
        )}
        {definition.values_count || 0} values
      </button>
      {expanded && (
        <div className="mt-2 pl-4">
          {isLoading ? (
            <div className="animate-pulse h-4 bg-gray-200 rounded w-24"></div>
          ) : values.length === 0 ? (
            <p className="text-sm text-gray-500">No values defined</p>
          ) : (
            values.map((value) => renderValue(value))
          )}
        </div>
      )}
    </div>
  );
}

export default function LabelsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState<LabelDefinition | null>(null);

  // Fetch label definitions
  const { data: labelsData, isLoading } = useQuery({
    queryKey: ['label-definitions'],
    queryFn: labelsApi.getLabelDefinitions,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: labelsApi.deleteLabelDefinition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['label-definitions'] });
    },
  });

  const handleEdit = (label: LabelDefinition) => {
    setSelectedLabel(label);
    setShowModal(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this label definition? All associated values will be deleted.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleCreate = () => {
    setSelectedLabel(null);
    setShowModal(true);
  };

  const labels = labelsData?.results || [];
  const labelsCount = labels.length;
  const remainingLabels = MAX_LABELS - labelsCount;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Labels</h1>
          <p className="mt-1 text-sm text-gray-500">Manage taxonomy and classification labels</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={handleCreate}
            disabled={labelsCount >= MAX_LABELS}
            className="btn btn-primary"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Label
          </button>
        </div>
      </div>

      {/* Labels limit warning */}
      <div className={`card p-4 ${remainingLabels <= 5 ? 'bg-yellow-50 border-yellow-200' : 'bg-gray-50'}`}>
        <div className="flex items-center">
          {remainingLabels <= 5 && (
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mr-2" />
          )}
          <div>
            <p className={`text-sm ${remainingLabels <= 5 ? 'text-yellow-700' : 'text-gray-600'}`}>
              <span className="font-medium">{labelsCount}</span> of {MAX_LABELS} labels used
              {remainingLabels <= 5 && ` (${remainingLabels} remaining)`}
            </p>
            <div className="mt-2 h-2 w-64 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  remainingLabels <= 5 ? 'bg-yellow-500' : 'bg-primary-500'
                }`}
                style={{ width: `${(labelsCount / MAX_LABELS) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Labels grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : labels.length === 0 ? (
        <div className="card text-center py-12">
          <TagIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p className="text-gray-500">No labels defined</p>
          <button onClick={handleCreate} className="btn btn-primary mt-4">
            Create your first label
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {labels.map((label: LabelDefinition) => (
            <div key={label.id} className="card p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center">
                    <TagIcon className="h-5 w-5 text-gray-500" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">{label.name}</h3>
                    <p className="text-sm text-gray-500">{label.code}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleEdit(label)}
                    className="p-1 hover:bg-gray-100 rounded-lg"
                  >
                    <PencilIcon className="h-4 w-4 text-gray-500" />
                  </button>
                  <button
                    onClick={() => handleDelete(label.id)}
                    className="p-1 hover:bg-gray-100 rounded-lg"
                  >
                    <TrashIcon className="h-4 w-4 text-red-500" />
                  </button>
                </div>
              </div>

              {label.description && (
                <p className="mt-3 text-sm text-gray-600">{label.description}</p>
              )}

              <div className="mt-4 flex flex-wrap gap-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeColors[label.label_type]}`}>
                  {label.label_type}
                </span>
                {label.is_required && (
                  <span className="badge badge-danger">Required</span>
                )}
                {!label.is_active && (
                  <span className="badge badge-secondary">Inactive</span>
                )}
                {label.is_hierarchical && (
                  <span className="badge badge-info">{label.max_levels} levels</span>
                )}
              </div>

              <LabelValueTree definition={label} />
            </div>
          ))}
        </div>
      )}

      {/* Label Modal */}
      <LabelModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedLabel(null);
        }}
        label={selectedLabel}
        currentCount={labelsCount}
      />
    </div>
  );
}
