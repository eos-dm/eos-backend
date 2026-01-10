/**
 * EOS Platform - Clients Admin Page
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { coreApi } from '@/services/api';
import type { Client, CostCenter } from '@/types';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  BuildingOfficeIcon,
  EllipsisVerticalIcon,
} from '@heroicons/react/24/outline';

// Create/Edit Client Modal
interface ClientModalProps {
  isOpen: boolean;
  onClose: () => void;
  client?: Client | null;
  costCenters: CostCenter[];
}

function ClientModal({ isOpen, onClose, client, costCenters }: ClientModalProps) {
  const queryClient = useQueryClient();
  const isEditing = !!client;
  const [formData, setFormData] = useState({
    cost_center: client?.cost_center?.toString() || '',
    name: client?.name || '',
    code: client?.code || '',
    contact_name: client?.contact_name || '',
    contact_email: client?.contact_email || '',
    contact_phone: client?.contact_phone || '',
    is_active: client?.is_active ?? true,
  });
  const [error, setError] = useState('');

  const createMutation = useMutation({
    mutationFn: coreApi.createClient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create client');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<Client>) => coreApi.updateClient(client!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update client');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const data = {
      cost_center: parseInt(formData.cost_center),
      name: formData.name,
      code: formData.code,
      contact_name: formData.contact_name || undefined,
      contact_email: formData.contact_email || undefined,
      contact_phone: formData.contact_phone || undefined,
      is_active: formData.is_active,
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
            {isEditing ? 'Edit Client' : 'Create New Client'}
          </h3>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cost Center</label>
              <select
                value={formData.cost_center}
                onChange={(e) => setFormData({ ...formData, cost_center: e.target.value })}
                required
                className="input"
              >
                <option value="">Select cost center</option>
                {costCenters.map((cc) => (
                  <option key={cc.id} value={cc.id}>
                    {cc.name} ({cc.agency_name})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="input"
                  placeholder="Acme Corporation"
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
                  placeholder="ACME"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contact Name</label>
              <input
                type="text"
                value={formData.contact_name}
                onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                className="input"
                placeholder="John Smith"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contact Email</label>
                <input
                  type="email"
                  value={formData.contact_email}
                  onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                  className="input"
                  placeholder="contact@client.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contact Phone</label>
                <input
                  type="tel"
                  value={formData.contact_phone}
                  onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                  className="input"
                  placeholder="+34 600 000 000"
                />
              </div>
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
                Active client
              </label>
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
                  ? 'Update Client'
                  : 'Create Client'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function ClientsPage() {
  useQueryClient(); // Keep for cache invalidation in mutations
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  // Fetch clients
  const { data: clientsData, isLoading } = useQuery({
    queryKey: ['clients', { search: searchTerm }],
    queryFn: () => coreApi.getClients({ search: searchTerm || undefined }),
  });

  // Fetch cost centers for modal
  const { data: costCentersData } = useQuery({
    queryKey: ['cost-centers'],
    queryFn: () => coreApi.getCostCenters(),
  });

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setShowModal(true);
    setOpenMenuId(null);
  };

  const handleCreate = () => {
    setSelectedClient(null);
    setShowModal(true);
  };

  const clients = clientsData?.results || [];
  const costCenters = costCentersData?.results || [];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
          <p className="mt-1 text-sm text-gray-500">Manage client accounts</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button onClick={handleCreate} className="btn btn-primary">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Client
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="relative max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search clients..."
            className="input pl-10"
          />
        </div>
      </div>

      {/* Clients grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : clients.length === 0 ? (
        <div className="card text-center py-12">
          <BuildingOfficeIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p className="text-gray-500">No clients found</p>
          <button onClick={handleCreate} className="btn btn-primary mt-4">
            Add your first client
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clients.map((client: Client) => (
            <div key={client.id} className="card p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  {client.logo ? (
                    <img
                      src={client.logo}
                      alt={client.name}
                      className="h-12 w-12 rounded-lg object-cover"
                    />
                  ) : (
                    <div className="h-12 w-12 rounded-lg bg-gray-100 flex items-center justify-center">
                      <BuildingOfficeIcon className="h-6 w-6 text-gray-400" />
                    </div>
                  )}
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">{client.name}</h3>
                    <p className="text-sm text-gray-500">{client.code}</p>
                  </div>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setOpenMenuId(openMenuId === client.id ? null : client.id)}
                    className="p-1 hover:bg-gray-100 rounded-lg"
                  >
                    <EllipsisVerticalIcon className="h-5 w-5 text-gray-500" />
                  </button>

                  {openMenuId === client.id && (
                    <>
                      <div
                        className="fixed inset-0 z-40"
                        onClick={() => setOpenMenuId(null)}
                      />
                      <div className="absolute right-0 z-50 mt-2 w-48 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5">
                        <div className="py-1">
                          <button
                            onClick={() => handleEdit(client)}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <PencilIcon className="h-4 w-4 mr-3" />
                            Edit
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Agency</span>
                  <span className="text-gray-900">{client.agency_name || '-'}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Cost Center</span>
                  <span className="text-gray-900">{client.cost_center_name || '-'}</span>
                </div>
                {client.contact_name && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Contact</span>
                    <span className="text-gray-900">{client.contact_name}</span>
                  </div>
                )}
                {client.contact_email && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Email</span>
                    <a
                      href={`mailto:${client.contact_email}`}
                      className="text-primary-600 hover:text-primary-800"
                    >
                      {client.contact_email}
                    </a>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-100">
                <span
                  className={`badge ${client.is_active ? 'badge-success' : 'badge-secondary'}`}
                >
                  {client.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Client Modal */}
      <ClientModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedClient(null);
        }}
        client={selectedClient}
        costCenters={costCenters}
      />
    </div>
  );
}
