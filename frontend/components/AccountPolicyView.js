import React, { useState, useMemo, useEffect, useRef } from 'react';
import Link from 'next/link';

/**
 * Simple collapse/expand section without external dependencies.
 */
function CollapseSection({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="mb-4">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex w-full justify-between items-center bg-[#0c0d15] px-3 py-2 rounded"
      >
        <span className="text-white">{title}</span>
        <span className="text-gray-400">{open ? '▾' : '▸'}</span>
      </button>
      {open && <div className="mt-2 pl-4">{children}</div>}
    </div>
  );
}

/**
 * Renders a hierarchical view of accounts, policies, departments, claims, and documents.
 * Shows a toast when new documents arrive and includes a manual refresh button.
 * @param {{ data: Array, onRefresh: Function }} props
 */
export default function AccountPolicyView({ data, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [toastVisible, setToastVisible] = useState(false);
  const prevDocIdsRef = useRef(new Set());

  // Show “New documents arrived” toast when data prop gains new doc IDs
  useEffect(() => {
    const currentIds = new Set();
    data.forEach(acct =>
      acct.policies.forEach(pol =>
        pol.departments.forEach(dept => {
          if (dept.department === 'Claims') {
            dept.claims?.forEach(cl =>
              cl.documents.forEach(doc => currentIds.add(doc.id))
            );
          } else {
            dept.documents?.forEach(doc => currentIds.add(doc.id));
          }
        })
      )
    );

    const prevIds = prevDocIdsRef.current;
    if (prevIds.size > 0 && currentIds.size > prevIds.size) {
      setToastVisible(true);
      setTimeout(() => setToastVisible(false), 3000);
    }
    prevDocIdsRef.current = currentIds;
  }, [data]);

  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    const lower = searchTerm.toLowerCase();

    return data
      .map(acct => {
        const acctMatches =
          acct.account_number.toLowerCase().includes(lower) ||
          acct.policyholder_name.toLowerCase().includes(lower);

        const policies = acct.policies
          .map(pol => {
            const policyMatches = pol.policy_number
              .toLowerCase()
              .includes(lower);

            let departments = [];

            if (acctMatches || policyMatches) {
              departments = pol.departments;
            } else {
              const claimDept = pol.departments.find(d => d.department === 'Claims');
              if (claimDept) {
                const matchingClaims = claimDept.claims?.filter(cl =>
                  cl.claim_number.toLowerCase().includes(lower)
                );
                if (matchingClaims?.length) {
                  departments = [{ department: 'Claims', claims: matchingClaims }];
                }
              }
            }

            return departments.length ? { ...pol, departments } : null;
          })
          .filter(Boolean);

        return acctMatches || policies.length ? { ...acct, policies } : null;
      })
      .filter(Boolean);
  }, [data, searchTerm]);

  return (
    <div className="relative space-y-6 p-6">
      {/* Toast */}
      {toastVisible && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded shadow-lg">
          New documents arrived
        </div>
      )}

      {/* Refresh + Search */}
      <div className="flex justify-end mb-4 items-center">
        <button
          onClick={onRefresh}
          className="mr-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Refresh
        </button>
        <input
          type="text"
          placeholder="Search account, policy or claim #…"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="px-3 py-2 bg-white text-black border border-gray-300 rounded placeholder-gray-500"
        />
      </div>

      {filteredData.map(acct => {
        const lower = searchTerm.toLowerCase();
        const acctMatches =
          searchTerm &&
          (acct.account_number.toLowerCase().includes(lower) ||
            acct.policyholder_name.toLowerCase().includes(lower));

        return (
          <div
            key={acct.account_number}
            className="bg-[#1e1e2f] rounded-lg shadow-md"
          >
            <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Account: {acct.account_number}
                </h2>
                <p className="text-sm text-gray-400">
                  Policyholder: {acct.policyholder_name}
                </p>
              </div>
            </div>
            <div className="p-4">
              {acct.policies.map(pol => {
                const policyMatches =
                  searchTerm &&
                  pol.policy_number.toLowerCase().includes(lower);
                const claimMatchInPol =
                  searchTerm &&
                  pol.departments
                    .find(d => d.department === 'Claims')
                    ?.claims?.some(cl =>
                      cl.claim_number.toLowerCase().includes(lower)
                    );

                const policyOpen = !!(acctMatches || policyMatches || claimMatchInPol);

                return (
                  <CollapseSection
                    key={pol.policy_number}
                    title={`Policy #${pol.policy_number}`}
                    defaultOpen={policyOpen}
                  >
                    {pol.departments.map(dept => {
                      const isClaims = dept.department === 'Claims';
                      const deptHasMatch =
                        isClaims &&
                        searchTerm &&
                        dept.claims?.some(cl =>
                          cl.claim_number.toLowerCase().includes(lower)
                        );
                      const deptOpen = !!(acctMatches || policyMatches || deptHasMatch);

                      return (
                        <CollapseSection
                          key={dept.department}
                          title={dept.department}
                          defaultOpen={deptOpen}
                        >
                          {isClaims ? (
                            dept.claims.map(cl => {
                              const clMatches =
                                searchTerm &&
                                cl.claim_number.toLowerCase().includes(lower);
                              const claimOpen = !!clMatches;

                              return (
                                <CollapseSection
                                  key={cl.claim_number}
                                  title={
                                    <span
                                      className={
                                        clMatches
                                          ? 'text-blue-500 font-semibold'
                                          : ''
                                      }
                                    >
                                      Claim #{cl.claim_number}
                                    </span>
                                  }
                                  defaultOpen={claimOpen}
                                >
                                  <ul className="list-disc list-inside text-gray-300">
                                    {cl.documents.map(doc => {
                                      const ts = new Date(doc.updated_at)
                                        .toLocaleString("en-US", {
                                          dateStyle: "long",
                                          timeStyle: "medium",
                                          hour12: true
                                        });
                                      return (
                                        <li key={doc.id} className="py-1">
                                          <Link href={`/document/${doc.id}`}>
                                            <a className="hover:underline">
                                              {doc.filename} – {ts}
                                            </a>
                                          </Link>
                                        </li>
                                      );
                                    })}
                                  </ul>
                                </CollapseSection>
                              );
                            })
                          ) : (
                            <ul className="list-disc list-inside text-gray-300">
                              {dept.documents.map(doc => {
                                const ts = new Date(doc.updated_at)
                                  .toLocaleString("en-US", {
                                    dateStyle: "long",
                                    timeStyle: "medium",
                                    hour12: true
                                  });
                                return (
                                  <li key={doc.id} className="py-1">
                                    <Link href={`/document/${doc.id}`}>
                                      <a className="hover:underline">
                                        {doc.filename} – {ts}
                                      </a>
                                    </Link>
                                  </li>
                                );
                              })}
                            </ul>
                          )}
                        </CollapseSection>
                      );
                    })}
                  </CollapseSection>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
