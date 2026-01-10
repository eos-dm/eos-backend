/**
 * EOS Platform - Workflows Admin Page
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { workflowsApi } from '@/services/api';
import type { WorkflowDefinition, WorkflowState, EntityType } from '@/types';
import {
  ArrowPathIcon,
  PlusIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

// Entity type labels
const entityTypeLabels: Record<EntityType, string> = {
  campaign: 'Campaigns',
  media_plan: 'Media Plans',
  subcampaign: 'Subcampaigns',
  project: 'Projects',
};

// State type icons
function StateIcon({ stateType }: { stateType: string }) {
  switch (stateType) {
    case 'initial':
      return <ClockIcon className="h-4 w-4 text-blue-500" />;
    case 'final':
      return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
    default:
      return <ArrowPathIcon className="h-4 w-4 text-yellow-500" />;
  }
}

// Workflow States Display
function WorkflowStatesDisplay({ workflow }: { workflow: WorkflowDefinition }) {
  const [expanded, setExpanded] = useState(false);

  const states = workflow.states || [];
  const transitions = workflow.transitions || [];

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
        {states.length} states, {transitions.length} transitions
      </button>

      {expanded && (
        <div className="mt-4 space-y-4">
          {/* States */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">States</h4>
            <div className="space-y-2">
              {states
                .sort((a, b) => a.display_order - b.display_order)
                .map((state: WorkflowState) => (
                  <div
                    key={state.id}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center">
                      <StateIcon stateType={state.state_type} />
                      <span className="ml-2 text-sm text-gray-900">{state.name}</span>
                      <span className="ml-2 text-xs text-gray-500">({state.code})</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {state.requires_approval && (
                        <span className="badge badge-warning text-xs">Approval</span>
                      )}
                      {!state.is_editable && (
                        <span className="badge badge-secondary text-xs">Locked</span>
                      )}
                      <span
                        className={`badge text-xs ${
                          state.state_type === 'initial'
                            ? 'badge-info'
                            : state.state_type === 'final'
                            ? 'badge-success'
                            : 'badge-secondary'
                        }`}
                      >
                        {state.state_type}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Transitions visualization */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Transitions</h4>
            <div className="space-y-2">
              {transitions.map((transition: any) => {
                const fromState = states.find((s) => s.id === transition.from_state);
                const toState = states.find((s) => s.id === transition.to_state);
                return (
                  <div
                    key={transition.id}
                    className="flex items-center p-2 bg-gray-50 rounded-lg text-sm"
                  >
                    <span className="font-medium text-gray-700">{fromState?.name || '?'}</span>
                    <ChevronRightIcon className="h-4 w-4 mx-2 text-gray-400" />
                    <span className="font-medium text-gray-700">{toState?.name || '?'}</span>
                    <span className="ml-auto text-gray-500">{transition.name}</span>
                    {transition.requires_approval && (
                      <span className="ml-2 badge badge-warning text-xs">Approval</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function WorkflowsPage() {
  // Fetch workflow definitions
  const { data: workflowsData, isLoading } = useQuery({
    queryKey: ['workflow-definitions'],
    queryFn: workflowsApi.getWorkflowDefinitions,
  });

  const workflows = workflowsData?.results || [];

  // Group workflows by entity type
  const workflowsByEntity = workflows.reduce(
    (acc: Record<EntityType, WorkflowDefinition[]>, wf: WorkflowDefinition) => {
      if (!acc[wf.entity_type]) {
        acc[wf.entity_type] = [];
      }
      acc[wf.entity_type].push(wf);
      return acc;
    },
    {} as Record<EntityType, WorkflowDefinition[]>
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflows</h1>
          <p className="mt-1 text-sm text-gray-500">Manage approval workflows and state machines</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button className="btn btn-primary" disabled>
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Workflow
          </button>
        </div>
      </div>

      {/* Info card */}
      <div className="card p-4 bg-blue-50 border-blue-200">
        <div className="flex items-start">
          <ArrowPathIcon className="h-5 w-5 text-blue-500 mt-0.5 mr-3" />
          <div>
            <h3 className="text-sm font-medium text-blue-800">About Workflows</h3>
            <p className="mt-1 text-sm text-blue-700">
              Workflows define the lifecycle states and approval processes for campaigns, media plans, and other entities.
              Each entity type can have one default workflow that is automatically applied to new items.
            </p>
          </div>
        </div>
      </div>

      {/* Workflows by entity type */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : workflows.length === 0 ? (
        <div className="card text-center py-12">
          <ArrowPathIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p className="text-gray-500">No workflows defined</p>
          <p className="text-sm text-gray-400 mt-1">
            Workflows are configured by the system administrator
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {(Object.keys(entityTypeLabels) as EntityType[]).map((entityType) => {
            const entityWorkflows = workflowsByEntity[entityType] || [];
            if (entityWorkflows.length === 0) return null;

            return (
              <div key={entityType}>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  {entityTypeLabels[entityType]}
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {entityWorkflows.map((workflow: WorkflowDefinition) => (
                    <div
                      key={workflow.id}
                      className="card p-6 hover:shadow-lg transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-lg bg-primary-50 flex items-center justify-center">
                            <ArrowPathIcon className="h-5 w-5 text-primary-600" />
                          </div>
                          <div className="ml-3">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {workflow.name}
                            </h3>
                            <p className="text-sm text-gray-500">{workflow.code}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {workflow.is_default && (
                            <span className="badge badge-primary">Default</span>
                          )}
                          <span
                            className={`badge ${
                              workflow.is_active ? 'badge-success' : 'badge-secondary'
                            }`}
                          >
                            {workflow.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </div>

                      {workflow.description && (
                        <p className="mt-3 text-sm text-gray-600">{workflow.description}</p>
                      )}

                      <WorkflowStatesDisplay workflow={workflow} />
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pending approvals section */}
      <PendingApprovals />
    </div>
  );
}

// Pending Approvals Component
function PendingApprovals() {
  const { data: approvalsData, isLoading } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => workflowsApi.getApprovalRequests('pending'),
  });

  const approvals = approvalsData?.results || [];

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Approvals</h3>

      {isLoading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : approvals.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircleIcon className="h-12 w-12 mx-auto text-green-300 mb-2" />
          <p>No pending approvals</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Request
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Requested By
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Requested At
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Due Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {approvals.map((approval: any) => (
                <tr key={approval.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">
                    Workflow Instance #{approval.workflow_instance}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    User #{approval.requested_by}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(approval.requested_at).toLocaleDateString('es-ES')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {approval.due_date
                      ? new Date(approval.due_date).toLocaleDateString('es-ES')
                      : '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span className="badge badge-warning">Pending</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
