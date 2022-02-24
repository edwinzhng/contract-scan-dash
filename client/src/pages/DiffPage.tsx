import React, { useEffect, useState } from "react";
import styled from "styled-components";
import ReactDiffViewer from "react-diff-viewer";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

const API_BASE_URL = "https://rocketpooldata.com/api/";
const BASE_CONTRACT_ENDPOINT = "base_contract_code/";
const CONTRACT_CODE_ENDPOINT = "contract_code/";

interface IContract {
  name: string;
  base_contract: string;
}

const DiffPageWrapper = styled.div`
  border-radius: 16px;
  box-shadow: 0 0 30px #1c1e25;
  margin: 20px;
`;

const DiffPage = () => {
  const [searchParams] = useSearchParams();
  const diffName = searchParams.get("diff_name");
  const diffAddress = searchParams.get("addr");

  const [diffNameContract, setDiffNameContract] = useState<IContract>();
  const [addrContract, setAddrContract] = useState<IContract>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<[]>();

  useEffect(() => {
    axios
      .get<IContract>(API_BASE_URL + BASE_CONTRACT_ENDPOINT + diffName)
      .then((res) => setDiffNameContract(res.data))
      .catch();
    axios
      .get<IContract>(API_BASE_URL + CONTRACT_CODE_ENDPOINT + diffAddress)
      .then((res) => setAddrContract(res.data))
      .catch((reason) => setError(reason));
    setLoading(false);
  }, [diffName, diffAddress]);

  return (
    <DiffPageWrapper>
      {loading && "Loading..."}
      {!loading && error && <>{error}</>}
      {!loading && !error && (
        <ReactDiffViewer
          useDarkTheme={false}
          oldValue={diffNameContract?.base_contract}
          newValue={addrContract?.base_contract}
          leftTitle={diffNameContract?.name}
          rightTitle={addrContract?.name}
          splitView={true}
        />
      )}{" "}
    </DiffPageWrapper>
  );
};

export default DiffPage;
